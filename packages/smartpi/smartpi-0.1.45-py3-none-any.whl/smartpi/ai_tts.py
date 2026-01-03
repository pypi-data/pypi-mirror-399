# -*- coding: utf-8 -*-
from datetime import datetime
import time
import asyncio
import threading
import pyaudio
import os
import sys
import numpy as np

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 添加SDK路径（使用绝对路径）
sys.path.append(os.path.join(current_dir, "tencentcloud-speech-sdk-python"))

from common import credential
from tts import flowing_speech_synthesizer

# 调试日志开关
DEBUG_MODE = True  # 设置为True开启详细调试日志

# 全局AI语音合成对象
_ai_tts_instance = None

# 音频参数设置
AUDIO_FORMAT = pyaudio.paInt16  # 音频格式，16位PCM
CHANNELS = 1  # 单声道
RATE = 16000  # 采样率16kHz

# 全局运行状态标志
is_running = True


class TTSStreamListener(flowing_speech_synthesizer.FlowingSpeechSynthesisListener):
    """TTS合成回调监听器，处理合成结果和进度"""
    
    def __init__(self, tts_engine, loop):
        """初始化TTSStreamListener对象
        
        参数:
            tts_engine: TTS引擎实例，用于回调和状态更新
            loop: asyncio事件循环，用于音频队列操作
        """
        super().__init__()
        self.tts_engine = tts_engine
        self.loop = loop
        self.session_id = ""
        self.total_audio_bytes = 0
        self.bit_depth = 16
        
        # 文本片段拆分的字节数记录（用于计算每个片段的时长）
        self.current_chunk_bytes = 0  # 当前文本片段的音频字节数
        self.text_chunk_bytes = []    # 存储每个文本片段的音频字节数列表
        self.subtitle_data = []       # 存储字幕数据

    def on_synthesis_start(self, session_id):
        """合成开始时的回调
        
        参数:
            session_id: 会话ID
        """
        super().on_synthesis_start(session_id)
        self.session_id = session_id
        self.total_audio_bytes = 0
        self.current_chunk_bytes = 0
        self.text_chunk_bytes = []
        self.subtitle_data = []
        
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS合成开始|session_id: {session_id}")

    def on_synthesis_end(self):
        """合成结束时的回调"""
        super().on_synthesis_end()
        
        # 将最后一个片段的字节数加入列表（若有剩余）
        if self.current_chunk_bytes > 0:
            self.text_chunk_bytes.append(self.current_chunk_bytes)
            self.current_chunk_bytes = 0
        
        # 计算每个文本片段的时长并同步给TTS引擎
        chunk_durations = []
        for bytes_cnt in self.text_chunk_bytes:
            duration = bytes_cnt / (self.tts_engine.rate * self.tts_engine.channels * (self.bit_depth / 8))
            chunk_durations.append(round(duration, 2))
        self.tts_engine.text_chunk_durations = chunk_durations
        
        # 同步字幕数据到引擎
        self.tts_engine.subtitle_data = self.subtitle_data
        
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS合成结束|各片段时长: {chunk_durations}秒")
        
        self.tts_engine.on_synthesis_complete()

    def on_audio_result(self, audio_bytes):
        """收到音频结果时的回调
        
        参数:
            audio_bytes: 音频字节数据
        """
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|收到音频数据|长度: {len(audio_bytes)}字节")
        
        super().on_audio_result(audio_bytes)
        
        # 累加当前片段的音频字节数
        if audio_bytes:
            self.total_audio_bytes += len(audio_bytes)
            self.current_chunk_bytes += len(audio_bytes)
        
        if audio_bytes and self.tts_engine.audio_queue:
            asyncio.run_coroutine_threadsafe(
                self.tts_engine.audio_queue.put(audio_bytes),
                self.loop
            )

    def on_synthesis_fail(self, response):
        """合成失败时的回调
        
        参数:
            response: 包含错误信息的响应字典
        """
        super().on_synthesis_fail(response)
        err_code = response["code"]
        err_msg = response["message"]
        
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS合成失败|错误码: {err_code}|错误信息: {err_msg}")
        
        self.tts_engine.on_synthesis_complete()

    def on_text_result(self, response):
        """收到文本结果时的回调
        
        参数:
            response: 包含文本结果的响应字典
        """
        super().on_text_result(response)
        
        # 处理字幕数据
        if 'result' in response and 'subtitles' in response['result']:
            subtitles = response['result']['subtitles']
            if subtitles:
                for subtitle in subtitles:
                    # 提取每个字的信息
                    text = subtitle.get('Text', '')
                    begin_time = subtitle.get('BeginTime', 0)
                    end_time = subtitle.get('EndTime', 0)
                    begin_index = subtitle.get('BeginIndex', 0)
                    end_index = subtitle.get('EndIndex', 0)
                    
                    # 存储字幕数据
                    self.subtitle_data.append({
                        'text': text,
                        'begin_time': begin_time / 1000,  # 转换为秒
                        'end_time': end_time / 1000,      # 转换为秒
                        'begin_index': begin_index,
                        'end_index': end_index
                    })
                    
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|收到字幕数据|包含 {len(subtitles)} 个字")


class TencentSpeechSynthesizer:
    """腾讯云流式TTS合成器"""
    
    def __init__(self, appid=None, secret_id=None, secret_key=None):
        """初始化TencentSpeechSynthesizer对象
        
        参数:
            appid (str, optional): 腾讯云APPID
            secret_id (str, optional): 腾讯云SECRET_ID
            secret_key (str, optional): 腾讯云SECRET_KEY
        """
        self.state_lock = threading.Lock()
        self.appid = appid
        self.cred = credential.Credential(secret_id, secret_key) if secret_id and secret_key else None
        
        self.audio_format = AUDIO_FORMAT
        self.channels = CHANNELS
        self.rate = RATE
        
        self.listener = None
        self.synthesizer = None
        self.audio_queue = None
        self.p = None  # PyAudio实例
        self.playback_stream = None
        self.loop = None
        self.is_ready = False
        self.loop_thread = None
        self._is_playing = False
        self.synthesis_complete = False
        self.audio_duration = 0.0
        
        # 音量控制
        self.volume = 1.0  # 默认音量100%
        
        # 文本片段-音频时长映射
        self.text_chunk_durations = []  # 存储每个文本片段的时长
        self.current_chunk_index = 0    # 当前播放的文本片段索引
        self.subtitle_data = []         # 存储字幕数据
        
        # 回调函数
        self.on_play_start = None
        self.on_play_end = None
        
        # 初始化PyAudio实例
        self._init_pyaudio()
    
    def _init_pyaudio(self):
        """初始化PyAudio实例"""
        try:
            self.p = pyaudio.PyAudio()
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|PyAudio实例初始化成功")
        except Exception as e:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|PyAudio实例初始化失败|错误: {str(e)}")
            self.p = None

    @property
    def is_playing(self):
        """是否正在播放的属性
        
        返回:
            bool: True表示正在播放，False表示未在播放
        """
        with self.state_lock:
            return self._is_playing

    @is_playing.setter
    def is_playing(self, value):
        """设置播放状态
        
        参数:
            value (bool): 播放状态，True表示正在播放，False表示未在播放
        """
        with self.state_lock:
            self._is_playing = value
    
    def set_playback_callback(self, on_play_start=None, on_play_end=None):
        """设置播放回调函数
        
        参数:
            on_play_start (callable, optional): 播放开始时的回调函数
            on_play_end (callable, optional): 播放结束时的回调函数
        """
        self.on_play_start = on_play_start
        self.on_play_end = on_play_end

    def get_audio_duration(self):
        """获取音频总时长
        
        返回:
            float: 音频总时长（秒）
        """
        with self.state_lock:
            return self.audio_duration

    def get_current_chunk_duration(self):
        """获取当前播放片段的时长
        
        返回:
            float: 当前片段的时长（秒），如果没有片段则返回0.0
        """
        with self.state_lock:
            if self.current_chunk_index < len(self.text_chunk_durations):
                return self.text_chunk_durations[self.current_chunk_index]
            return 0.0

    def mark_chunk_played(self):
        """标记当前片段已播放完成
        
        返回:
            bool: True表示还有下一段，False表示所有片段已播放完
        """
        with self.state_lock:
            if self.current_chunk_index < len(self.text_chunk_durations) - 1:
                self.current_chunk_index += 1
                return True  # 还有下一段
            return False  # 所有片段已播放完

    def on_synthesis_complete(self):
        """合成完成回调"""
        self.synthesis_complete = True
        
        # 计算总合成时长
        if hasattr(self, 'text_chunk_durations') and self.text_chunk_durations:
            self.total_duration = sum(self.text_chunk_durations)
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|合成已完成|总时长: {self.total_duration:.2f}秒")
        else:
            self.total_duration = 0
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|合成已完成|无法计算总时长")

    def init(self):
        """初始化TTS合成器
        
        返回:
            bool: True表示初始化成功，False表示初始化失败
        """
        # 确保PyAudio实例有效
        if not self.p:
            self._init_pyaudio()
            if not self.p:
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|没有可用的PyAudio实例")
                return False
                
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.current_thread()
        asyncio.set_event_loop(self.loop)
        
        self.audio_queue = asyncio.Queue()
        self.listener = TTSStreamListener(self, self.loop)
        
        self.synthesizer = flowing_speech_synthesizer.FlowingSpeechSynthesizer(
            self.appid, self.cred, self.listener)
        self.synthesizer.set_voice_type(501000)
        self.synthesizer.set_codec("pcm")
        self.synthesizer.set_sample_rate(self.rate)
        self.synthesizer.set_enable_subtitle(True)
        
        self.synthesizer.start()
        # 等待5秒检查是否准备就绪
        self.is_ready = self.synthesizer.wait_ready(5000)
        if not self.is_ready:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS合成器准备超时，但继续初始化")
            # 即使超时也不立即清理，尝试继续使用
            self.is_ready = True  # 强制设置为就绪状态
        return self.is_ready

    def set_volume(self, volume):
        """设置音量
        
        参数:
            volume (float): 音量大小，范围0.0-1.0
            
        返回:
            tuple[bool, float]: (设置是否成功, 设置后的音量值)
        """
        try:
            volume_level = max(0.0, min(1.0, float(volume)))
            self.volume = volume_level
            
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS音量已设置|值: {volume_level * 100:.1f}%")
            
            return True, volume_level
        except Exception as e:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|设置音量失败|错误: {e}")
            return False, None
            
    def send_text_chunk(self, text, is_end=False):
        """发送文本片段进行合成
        
        参数:
            text (str): 要合成的文本片段
            is_end (bool, optional): 是否为最后一个文本片段，默认为False
        """
        if not self.synthesizer or not self.is_ready:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS未初始化完成，无法发送文本")
            return
        
        # 对于流式TTS，不要清空音频队列，让每个片段都能播放
        
        # 重置合成完成标志
        self.synthesis_complete = False
        
        try:
            # 检查WebSocket连接是否真正打开，如果已关闭则重新启动合成器
            if not self.synthesizer.ws or self.synthesizer.status in [3, 4, 5]:  # FINAL, ERROR, CLOSED
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|WebSocket连接已关闭，正在重新启动合成器...")
                
                # 重新创建合成器实例
                self.synthesizer = flowing_speech_synthesizer.FlowingSpeechSynthesizer(
                    self.appid, self.cred, self.listener)
                self.synthesizer.set_voice_type(501000)
                self.synthesizer.set_codec("pcm")
                self.synthesizer.set_sample_rate(self.rate)
                self.synthesizer.set_enable_subtitle(True)
                
                # 启动合成器
                self.synthesizer.start()
                
                # 等待连接打开，最多等待5秒
                start_time = time.time()
                while time.time() - start_time < 5:
                    if hasattr(self.synthesizer, 'ws') and self.synthesizer.ws and self.synthesizer.status == 2:  # OPENED
                        if DEBUG_MODE:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|WebSocket连接已重新打开")
                        break
                    time.sleep(0.1)
                
                # 如果仍然未打开，返回
                if not hasattr(self.synthesizer, 'ws') or not self.synthesizer.ws or self.synthesizer.status != 2:
                    if DEBUG_MODE:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|WebSocket连接未打开，无法发送文本")
                    return
            elif not self.synthesizer.ws or self.synthesizer.status != 2:  # 其他未打开状态
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|WebSocket连接未完全打开，等待...")
                # 等待连接打开，最多等待2秒
                start_time = time.time()
                while time.time() - start_time < 2:
                    if self.synthesizer.ws and self.synthesizer.status == 2:
                        break
                    time.sleep(0.1)
                
                # 如果仍然未打开，返回
                if not self.synthesizer.ws or self.synthesizer.status != 2:
                    if DEBUG_MODE:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|WebSocket连接未打开，无法发送文本")
                    return
            
            # 每次发送新文本片段前，记录上一段的字节数（若有）
            if self.listener and self.listener.current_chunk_bytes > 0:
                self.listener.text_chunk_bytes.append(self.listener.current_chunk_bytes)
                self.listener.current_chunk_bytes = 0
            
            self.synthesizer.process(text)
            if is_end:
                self.synthesizer.complete()
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|已发送合成完成指令")
        except Exception as e:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|发送文本失败|错误: {e}")

    def start_playback(self):
        """开始播放合成的音频"""
        def play():
            self.is_playing = True
            if self.on_play_start:
                threading.Thread(target=self.on_play_start, daemon=True).start()
            self.playback_thread = threading.current_thread()
            asyncio.set_event_loop(self.loop)
            
            try:
                # 确保PyAudio实例有效
                if not self.p:
                    self._init_pyaudio()
                    if not self.p:
                        if DEBUG_MODE:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|没有可用的PyAudio实例，无法播放音频")
                        self.is_playing = False
                        if self.on_play_end:
                            threading.Thread(target=self.on_play_end, daemon=True).start()
                        return
                
                # 尝试使用配置的采样率，如果失败则尝试其他常见采样率
                supported_rates = [self.rate, 44100, 48000, 8000, 22050]
                selected_rate = None
                
                for rate in supported_rates:
                    try:
                        # 尝试打开一个临时流来测试采样率
                        test_stream = self.p.open(
                            format=self.audio_format,
                            channels=self.channels,
                            rate=rate,
                            output=True,
                            frames_per_buffer=1024
                        )
                        test_stream.close()
                        selected_rate = rate
                        break
                    except Exception as e:
                        if DEBUG_MODE:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|采样率 {rate}Hz 不受支持|错误: {e}")
                        continue
                
                if selected_rate is None:
                    if DEBUG_MODE:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|没有找到支持的采样率")
                    self.is_playing = False
                    if self.on_play_end:
                        threading.Thread(target=self.on_play_end, daemon=True).start()
                    return
                
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|使用采样率: {selected_rate}Hz")
                
                # 使用找到的支持的采样率打开播放流
                self.playback_stream = self.p.open(
                    format=self.audio_format,
                    channels=self.channels,
                    rate=selected_rate,
                    output=True
                )
                
                while is_running and (self.is_playing or not self.audio_queue.empty() or not self.synthesis_complete):
                    try:
                        audio_data = self.loop.run_until_complete(
                            asyncio.wait_for(self.audio_queue.get(), timeout=0.5)
                        )
                        
                        # 应用音量增益
                        if self.volume != 1.0:
                            # 仅当音量不是100%时进行处理
                            if self.audio_format == pyaudio.paInt16:
                                # 转换为numpy数组进行音量调整
                                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                                # 应用音量增益
                                adjusted_array = (audio_array * self.volume).astype(np.int16)
                                # 转换回字节流
                                audio_data = adjusted_array.tobytes()
                        
                        self.playback_stream.write(audio_data)
                        self.audio_queue.task_done()
                    except asyncio.TimeoutError:
                        if self.synthesis_complete and self.audio_queue.empty():
                            break
                        continue
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        if DEBUG_MODE:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|播放错误|错误: {e}")
                        break
                    
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|播放循环已退出")
                
            finally:
                if self.playback_stream:
                    try:
                        self.playback_stream.stop_stream()
                        self.playback_stream.close()
                    except Exception as e:
                        if DEBUG_MODE:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|关闭音频流时发生错误|错误: {e}")
                    finally:
                        self.playback_stream = None
                
                self.is_playing = False
                # 播放结束时，标记当前片段完成（确保字幕同步收尾）
                self.mark_chunk_played()
                if self.on_play_end:
                    threading.Thread(target=self.on_play_end, daemon=True).start()
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|播放已停止")
        
        threading.Thread(target=play, daemon=True).start()

    def stop_playback(self):
        """停止TTS播放并清理资源"""
        if not self.is_playing:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|播放已停止或未开始")
            return
            
        try:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|尝试停止TTS播放")
            
            self.is_playing = False
            
            # 清空音频队列
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                    self.audio_queue.task_done()
                except Exception:
                    break
            
            # 如果合成器正在运行，发送完成指令
            if self.synthesizer and not self.synthesis_complete:
                self.synthesizer.complete()
            
            # 停止时清空片段状态
            with self.state_lock:
                self.current_chunk_index = 0
                self.text_chunk_durations = []
            
            # 立即标记合成为完成状态，中断合成流程
            self.synthesis_complete = True
            
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS播放已停止")
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|停止播放失败|错误: {e}")

    def cleanup(self):
        """清理TTS资源"""
        global _ai_tts_instance
        
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|正在清理TTS资源")
        
        try:
            # 停止播放
            self.stop_playback()
            
            # 清理合成器
            if self.synthesizer:
                self.synthesizer.wait()
                self.synthesizer = None
            
            # 关闭事件循环
            if self.loop and not self.loop.is_closed():
                async def safe_shutdown():
                    await self.audio_queue.join()
                    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                    self.loop.stop()
        
                self.loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(safe_shutdown())
                )
        
                if threading.current_thread() != self.loop_thread:
                    while not self.loop.is_closed():
                        time.sleep(0.1)
            
            # 释放PyAudio实例
            if self.p:
                try:
                    self.p.terminate()
                except Exception:
                    pass
                finally:
                    self.p = None
            
            # 重置状态
            self.is_ready = False
            self.listener = None
            
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS资源清理完成")
            
            # 释放全局实例
            if _ai_tts_instance is self:
                _ai_tts_instance = None
                
        except Exception as e:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|清理TTS资源失败|错误: {e}")
        
    def blocking_synthesize_and_play(self, text, volume=None, rate=1.0, voice_type=1, platform="qcloud"):
        """阻塞式TTS合成与播放
        
        参数:
            text (str): 要合成的文本
            volume (float, optional): 音量，范围0.0-1.0，None表示使用当前设置
            rate (float, optional): 语速，范围0.1-3.0，默认为1.0
            voice_type (int, optional): 音色类型，默认为1
            platform (str, optional): 合成平台，默认为"qcloud"
            
        返回:
            bool: 播放是否成功
        """
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|开始阻塞式TTS合成与播放|文本: {text[:50]}...")
        
        # 存储原始设置
        original_volume = self.volume
        volume_changed = False
        
        try:
            # 设置音量（如果提供了参数）
            if volume is not None:
                self.set_volume(volume)
                volume_changed = True
            
            # 等待播放完成的事件
            play_completed_event = threading.Event()
            
            # 定义播放结束回调
            def on_playback_end():
                play_completed_event.set()
            
            # 设置回调
            self.on_play_end = on_playback_end
            
            # 初始化播放流
            if not self.is_playing:
                self.start_playback()
            
            # 发送文本进行合成
            self.send_text_chunk(text, is_end=True)
            
            # 等待播放完成
            play_completed_event.wait(timeout=60)  # 最多等待60秒
            
            if play_completed_event.is_set():
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|阻塞式播放已完成")
            else:
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|阻塞式播放超时")
                
            return True
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|阻塞式TTS合成与播放失败|错误: {e}")
            self.stop_playback()
            return False
            
        finally:
            # 恢复原始音量（仅当明确设置了音量时）
            if volume_changed:
                self.set_volume(original_volume)
            # 清空回调
            self.on_play_end = None


def init(secret_id, secret_key, app_id, volume=1) -> bool:
    """初始化TTS引擎
    
    参数:
        secret_id (str): 腾讯云API密钥ID
        secret_key (str): 腾讯云API密钥Key
        app_id (str): 腾讯云应用ID
        volume (float, optional): 初始音量，范围0.0-1.0，默认为1
        
    返回:
        bool: 初始化成功返回True，失败返回False
    """
    global _ai_tts_instance
    
    if DEBUG_MODE:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|初始化TTS引擎|app_id: {app_id}")
    
    try:
        if _ai_tts_instance is not None:
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS实例已存在，先清理资源")
            _ai_tts_instance.cleanup()
        
        _ai_tts_instance = TencentSpeechSynthesizer(app_id, secret_id, secret_key)
        
        # 设置初始音量
        if volume != 1:
            _ai_tts_instance.set_volume(volume)
        
        # 调用内部init方法完成真正的初始化
        if not _ai_tts_instance.init():
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS引擎内部初始化失败")
            return False
        
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS引擎初始化成功")
        return True
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS引擎初始化失败|错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def speak(text: str, is_end: bool = True) -> None:
    """开始TTS合成与播放
    
    参数:
        text (str): 要合成的文本
        is_end (bool, optional): 是否为最后一个文本片段，默认为True
    """
    global _ai_tts_instance
    
    if _ai_tts_instance is None:
        print("TTS未初始化，请先调用 init() 函数")
        return
    
    try:
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|开始TTS合成与播放|文本: {text[:50]}...")
        
        # 如果还没有开始播放，先启动播放线程
        if not _ai_tts_instance.is_playing:
            _ai_tts_instance.start_playback()
        
        # 发送文本进行合成
        _ai_tts_instance.send_text_chunk(text, is_end=is_end)
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS播放失败|错误: {e}")


def speak_blocking(text: str, volume: float = None) -> bool:
    """阻塞式TTS合成与播放
    
    参数:
        text (str): 要合成的文本
        volume (float, optional): 音量，范围0.0-1.0，默认使用当前设置
        
    返回:
        bool: 播放是否成功
    """
    global _ai_tts_instance
    
    if _ai_tts_instance is None:
        print("TTS未初始化，请先调用 init() 函数")
        return False
    
    try:
        # 如果指定了音量，先保存原始音量，播放后恢复
        original_volume = None
        if volume is not None:
            original_volume = _ai_tts_instance.volume
            _ai_tts_instance.set_volume(volume)
        
        # 使用阻塞式播放
        result = _ai_tts_instance.blocking_synthesize_and_play(text)
        
        # 恢复原始音量
        if original_volume is not None:
            _ai_tts_instance.set_volume(original_volume)
        
        return result
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|阻塞式TTS播放失败|错误: {e}")
        return False


def stop() -> None:
    """停止TTS播放
    
    返回:
        None
    """
    global _ai_tts_instance
    
    if _ai_tts_instance is None:
        print("TTS未初始化")
        return
    
    if DEBUG_MODE:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|停止TTS播放")
    
    _ai_tts_instance.stop_playback()


def set_volume(volume: float) -> bool:
    """设置TTS音量
    
    参数:
        volume (float): 音量大小，范围0.0-1.0
        
    返回:
        bool: 设置是否成功
    """
    global _ai_tts_instance
    
    if _ai_tts_instance is None:
        print("TTS未初始化，请先调用 init() 函数")
        return False
    
    success, _ = _ai_tts_instance.set_volume(volume)
    return success


def is_speaking() -> bool:
    """检查TTS是否正在播放
    
    返回:
        bool: 如果正在播放返回True，否则返回False
    """
    global _ai_tts_instance
    
    if _ai_tts_instance is None:
        return False
    
    return _ai_tts_instance.is_playing

def set_playback_callback(on_play_start=None, on_play_end=None) -> None:
    """设置播放回调函数
    
    参数:
        on_play_start (callable, optional): 播放开始时的回调函数
        on_play_end (callable, optional): 播放结束时的回调函数
    """
    global _ai_tts_instance
    
    if _ai_tts_instance is not None:
        _ai_tts_instance.set_playback_callback(on_play_start, on_play_end)


def release() -> None:
    """释放TTS资源
    
    返回:
        None
    """
    global _ai_tts_instance
    
    if _ai_tts_instance is not None:
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|释放TTS资源")
        _ai_tts_instance.cleanup()
        _ai_tts_instance = None
    else:
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|TTS实例不存在")


# 如果直接运行该文件，提供简单的测试功能
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("用法: python ai_tts.py <app_id> <secret_id> <secret_key> [文本]")
        sys.exit(1)
    
    app_id = sys.argv[1]
    secret_id = sys.argv[2]
    secret_key = sys.argv[3]
    text = "欢迎使用腾讯云TTS服务" if len(sys.argv) < 5 else sys.argv[4]
    
    # 初始化TTS
    if not init(secret_id, secret_key, app_id):
        print("TTS初始化失败")
        sys.exit(1)
    
    # 开始播放
    print(f"开始播放文本: {text}")
    speak_blocking(text)
    
    print("播放完成")
    release()