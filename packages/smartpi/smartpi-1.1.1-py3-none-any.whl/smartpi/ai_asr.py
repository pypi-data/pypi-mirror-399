# -*- coding: utf-8 -*-
import time

import threading
from datetime import datetime
import json
import os
import pyaudio
import wave
from threading import Event
import sys
import os

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 添加SDK路径（使用绝对路径）
sys.path.append(os.path.join(current_dir, "tencentcloud-speech-sdk-python"))
from common import credential
from asr import speech_recognizer

# 延迟导入VAD模块，减少启动时间
ai_vad = None

# 调试日志开关
DEBUG_MODE = False  # 设置为True开启详细调试日志

# 全局AI语音识别对象
_ai_asr_instance = None

class Connection:
    """用于存储VAD状态的连接类"""
    
    def __init__(self):
        """初始化Connection对象"""
        self.client_voice_stop = False  # 语音是否停止的标志
    
    def reset_vad_states(self) -> None:
        """重置VAD状态
        
        返回值:
            None
        """
        self.client_voice_stop = False

# 音频参数设置
FORMAT = pyaudio.paInt16  # 音频格式，16位PCM
CHANNELS = 1  # 单声道
RATE = 16000  # 采样率16kHz
CHUNK = 1024  # 每次读取的音频块大小
SLICE_SIZE = 6400  # SDK要求的分片大小


class MicrophoneSpeechListener(speech_recognizer.SpeechRecognitionListener):
    """语音识别回调监听器，处理并存储识别结果"""
    
    def __init__(self, sentence_callback=None):
        """初始化MicrophoneSpeechListener对象
        
        参数:
            sentence_callback (callable, optional): 句子识别完成后的回调函数，接收一个字符串参数
        """
        self.sentence_callback = sentence_callback  # 句子识别完成后的回调函数
        self.final_result = ""  # 最终识别结果
        self.interim_result = ""  # 中间识别结果
        self.is_recognizing = False  # 是否正在识别的标志
        self.lock = threading.Lock()  # 添加线程锁，保护共享变量的读写
        self.timestamps = {}  # 用于跟踪各个步骤的时间戳，用于调试

    def on_recognition_start(self, response: dict) -> None:
        """识别开始时的回调
        
        参数:
            response (dict): 包含识别开始信息的响应字典
        
        返回值:
            None
        """
        with self.lock:
            self.is_recognizing = True
        
        # 记录开始时间和调试信息
        start_time = time.time()
        self.timestamps['recognition_start'] = start_time
        
        if DEBUG_MODE:
            voice_id = response.get('voice_id', '未知')
            print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|识别开始|voice_id: {voice_id}|耗时: 0.00ms")

    def on_sentence_begin(self, response: dict) -> None:
        """句子开始时的回调
        
        参数:
            response (dict): 包含句子开始信息的响应字典
        
        返回值:
            None
        """
        # 记录时间和计算耗时
        current_time = time.time()
        self.timestamps['sentence_begin'] = current_time
        
        # 计算从识别开始到句子开始的耗时
        if 'recognition_start' in self.timestamps:
            elapsed = (current_time - self.timestamps['recognition_start']) * 1000
        else:
            elapsed = 0.0
            
        if DEBUG_MODE:
            rsp_str = json.dumps(response, ensure_ascii=False)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|句子开始|耗时: {elapsed:.2f}ms|{rsp_str}")

    def on_recognition_result_change(self, response: dict) -> None:
        """识别结果变化时的回调
        
        参数:
            response (dict): 包含最新识别结果的响应字典
        
        返回值:
            None
        """
        # 记录时间和计算耗时
        current_time = time.time()
        self.timestamps['result_change'] = current_time
        
        # 计算从句子开始到结果变化的耗时
        if 'sentence_begin' in self.timestamps:
            elapsed = (current_time - self.timestamps['sentence_begin']) * 1000
        else:
            elapsed = 0.0
            
        if DEBUG_MODE:
            rsp_str = json.dumps(response, ensure_ascii=False)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|结果更新|耗时: {elapsed:.2f}ms|{rsp_str}")
        
        # 提取中间结果
        if "result" in response and "voice_text_str" in response["result"]:
            with self.lock:
                self.interim_result = response["result"]["voice_text_str"]
            # 打印实时结果，不换行（此为功能输出，不受DEBUG_MODE控制）
            print(f"\r识别中: {self.interim_result}", end="")
        elif not DEBUG_MODE:  # 只有在非调试模式下才打印非结果更新的响应
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|结果更新|{rsp_str}")

    def on_sentence_end(self, response: dict) -> None:
        """句子结束时的回调
        
        参数:
            response (dict): 包含句子结束信息的响应字典
        
        返回值:
            None
        """
        # 记录时间和计算耗时
        current_time = time.time()
        self.timestamps['sentence_end'] = current_time
        
        # 计算从句子开始到句子结束的耗时
        if 'sentence_begin' in self.timestamps:
            elapsed = (current_time - self.timestamps['sentence_begin']) * 1000
        else:
            elapsed = 0.0
            
        if DEBUG_MODE:
            rsp_str = json.dumps(response, ensure_ascii=False)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|句子结束|耗时: {elapsed:.2f}ms|{rsp_str}")
        
        # 提取最终结果
        if "result" in response and "voice_text_str" in response["result"]:
            sentence = response["result"]["voice_text_str"]
            with self.lock:
                self.final_result += sentence
            
            # 打印句子识别完成信息（此为功能输出，不受DEBUG_MODE控制）
            print(f"\n句子识别完成: {sentence}")
            
            # 调用回调函数处理这个句子
            if self.sentence_callback:
                # 在新线程中调用回调，避免阻塞识别过程
                threading.Thread(target=self.sentence_callback, args=(sentence,), daemon=True).start()
        elif not DEBUG_MODE:  # 只有在非调试模式下才打印非结果的响应
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|句子结束|{rsp_str}")

    def on_recognition_complete(self, response: dict) -> None:
        """识别完成时的回调
        
        参数:
            response (dict): 包含识别完成信息的响应字典
        
        返回值:
            None
        """
        with self.lock:
            self.is_recognizing = False
        
        # 记录时间和计算耗时
        current_time = time.time()
        
        # 计算总耗时
        if 'recognition_start' in self.timestamps:
            total_elapsed = (current_time - self.timestamps['recognition_start']) * 1000
        else:
            total_elapsed = 0.0
            
        if DEBUG_MODE:
            voice_id = response.get('voice_id', '未知')
            print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|识别完成|voice_id: {voice_id}|总耗时: {total_elapsed:.2f}ms")
            print(f"最终识别结果: {self.final_result}")

    def on_fail(self, response: dict) -> None:
        """识别失败时的回调
        
        参数:
            response (dict): 包含识别失败信息的响应字典
        
        返回值:
            None
        """
        with self.lock:
            self.is_recognizing = False
        
        # 记录时间和计算耗时
        current_time = time.time()
        
        # 计算总耗时
        if 'recognition_start' in self.timestamps:
            total_elapsed = (current_time - self.timestamps['recognition_start']) * 1000
        else:
            total_elapsed = 0.0
            
        rsp_str = json.dumps(response, ensure_ascii=False)
        print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|识别失败|总耗时: {total_elapsed:.2f}ms|{rsp_str}")
        
        # 处理错误码4008（客户端超过15秒未发送音频数据），重启语音识别
        if 'code' in response and response['code'] == 4008:
            print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|检测到错误码4008，正在重启语音识别...")
            # 获取全局ASR实例并重启
            global _ai_asr_instance
            if _ai_asr_instance:
                try:
                    _ai_asr_instance.stop()
                    time.sleep(1)  # 增加延迟时间，确保资源完全释放
                    _ai_asr_instance.start()
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|语音识别已成功重启")
                except Exception as e:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|语音识别重启失败: {e}")
                    import traceback
                    traceback.print_exc()
                    # 如果重启失败，尝试重新创建ASR实例
                    try:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|尝试重新创建ASR实例...")
                        # 重新初始化ASR实例
                        from smartpi.ai_asr import init
                        # 使用原有的初始化参数重新初始化
                        init(
                            appid=_ai_asr_instance.appid,
                            secret_id=_ai_asr_instance.secret_id,
                            secret_key=_ai_asr_instance.secret_key,
                            sentence_callback=_ai_asr_instance.listener.sentence_callback,
                            engine_model_type=_ai_asr_instance.engine_model_type
                        )
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|ASR实例已重新创建")
                    except Exception as e2:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|重新创建ASR实例失败: {e2}")
                        import traceback
                        traceback.print_exc()
    
    def get_final_result(self) -> str:
        """获取当前的最终识别结果
        
        返回值:
            str: 最终识别结果字符串
        """
        with self.lock:
            return self.final_result

    def get_interim_result(self) -> str:
        """获取当前的中间识别结果
        
        返回值:
            str: 中间识别结果字符串
        """
        with self.lock:
            return self.interim_result

    def clear_results(self) -> None:
        """清除当前的识别结果
        
        返回值:
            None
        """
        start_time = time.time()
        with self.lock:
            self.final_result = ""
            self.interim_result = ""
        
        elapsed = (time.time() - start_time) * 1000
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|清除结果|耗时: {elapsed:.2f}ms")


class TencentSpeechRecognizer:
    """腾讯云语音识别封装类，提供开始、停止、暂停和恢复的接口"""
    
    def __init__(self, appid: str, secret_id: str, secret_key: str, 
                 engine_model_type: str = "16k_zh", 
                 sentence_callback=None, vad=None, 
                 interruption_callback=None):
        """初始化TencentSpeechRecognizer对象
        
        参数:
            appid (str): 腾讯云应用ID
            secret_id (str): 腾讯云Secret ID
            secret_key (str): 腾讯云Secret Key
            engine_model_type (str, optional): 引擎模型类型，默认"16k_zh"
            sentence_callback (callable, optional): 句子识别完成后的回调函数
            vad (object, optional): 语音活动检测(VAD)对象
            interruption_callback (callable, optional): 打断回调函数
        """
        self.appid = appid  # 腾讯云应用ID
        self.secret_id = secret_id  # 腾讯云Secret ID
        self.secret_key = secret_key  # 腾讯云Secret Key
        self.engine_model_type = engine_model_type  # 引擎模型类型
        
        # 初始化监听器，传入句子回调函数
        self.listener = MicrophoneSpeechListener(sentence_callback)
        self.credential = credential.Credential(self.secret_id,  self.secret_key )  # 腾讯云凭证
        self.recognizer = None  # 语音识别器实例
        self.capture_thread = None  # 麦克风采集线程
        self.stop_event = Event()  # 停止事件
        self.pause_event = Event()  # 用于控制暂停状态的事件
        self.is_running = False  # 是否正在运行的标志
        self.is_paused = False  # 是否处于暂停状态的标志
        
        # VAD相关
        self.vad = vad  # 语音活动检测(VAD)对象
        self.connection = Connection() if vad else None  # VAD状态连接对象
        
        # 打断回调函数，当检测到用户说话且需要打断当前活动时调用
        self.interruption_callback = interruption_callback
        self.lock = threading.Lock()  # 添加线程锁，保护共享状态变量的读写

    def _microphone_audio_capture(self) -> None:
        """麦克风音频采集线程函数
        
        返回值:
            None
        """
        p = pyaudio.PyAudio()
        stream = None  # 初始化流为None
        audio_buffer = b""  # 音频缓冲区，在try块之前初始化，防止finally块引用未定义变量
        try:
            # 打开麦克风流（指定输入设备，避免默认设备错误）
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=None,  # 自动选择默认设备，可改为具体设备索引
                frames_per_buffer=CHUNK
            )

            print("开始录音... 按Ctrl+C停止")
            # 用于跟踪上次发送数据的时间，防止连接超时
            last_send_time = time.time()
            
            # 重置VAD状态
            if self.connection:
                self.connection.reset_vad_states()
            
            while not self.stop_event.is_set():
                # 检查是否处于暂停状态，如果是则等待
                if self.pause_event.is_set():
                    self.is_paused = True
                    # 暂停时清空缓冲区，避免恢复后处理旧数据
                    audio_buffer = b""
                    # 重置VAD状态
                    if self.connection:
                        self.connection.reset_vad_states()
                    # 短暂休眠减少CPU占用
                    time.sleep(0.1)
                    continue
                
                if self.is_paused:
                    # 从暂停状态恢复
                    self.is_paused = False
                    print("\n语音识别已恢复")
                    # 恢复时重新开始计时
                    last_send_time = time.time()
                    # 重置VAD状态
                    if self.connection:
                        self.connection.reset_vad_states()
                
                try:
                    # 读取音频数据（添加超时和溢出处理）
                    data = stream.read(CHUNK, exception_on_overflow=False)  # 禁止溢出时抛异常
                    
                    # VAD检测
                    if self.vad and self.connection:
                        # 使用VAD检测语音
                        have_voice = self.vad.is_vad(self.connection, data)
                        
                        # 检查语音是否结束
                        if self.connection.client_voice_stop:
                            print("\nVAD检测到语音结束")
                            # 发送剩余的音频数据
                            if len(audio_buffer) > 0 and self.recognizer:
                                try:
                                    self.recognizer.write(audio_buffer)
                                    audio_buffer = b""
                                    # 发送尾包通知服务端识别结束
                                    self.recognizer.write(b"")
                                    last_send_time = time.time()
                                    print("\n已发送尾包，通知服务端识别结束")
                                except Exception as e:
                                    print(f"发送音频数据失败: {e}")
                            
                            # 确保识别完成并获取结果
                            if self.listener and hasattr(self.listener, 'final_result') and self.listener.final_result:
                                final_result = self.listener.final_result
                                print(f"[VAD触发] 处理最终识别结果: {final_result}")
                                # 直接调用句子回调函数处理结果
                                if hasattr(self.listener, 'sentence_callback') and self.listener.sentence_callback:
                                    threading.Thread(target=self.listener.sentence_callback, args=(final_result,), daemon=True).start()
                            # 重置监听器的结果
                            if self.listener:
                                self.listener.final_result = ""
                                self.listener.interim_result = ""
                            # 重新创建识别器准备下一次识别
                            self._recreate_recognizer()
                            # 重置VAD状态
                            self.connection.reset_vad_states()
                            # 短暂休眠避免频繁处理
                            time.sleep(0.01)
                            continue
                        
                        # 只有在检测到语音时才添加到缓冲区
                        if have_voice:
                            audio_buffer += data
                            # 检查是否需要打断当前活动
                            if self.interruption_callback and hasattr(self.connection, 'client_have_voice') and self.connection.client_have_voice:
                                print("[VAD检测] 用户开始说话，检查是否需要打断")
                                # 立即调用打断回调函数
                                threading.Thread(target=self.interruption_callback, daemon=True).start()
                    else:
                        # 没有VAD时，直接添加到缓冲区
                        audio_buffer += data
                    
                    current_time = time.time()
                    # 检查是否超过13秒未发送数据（提前2秒防止超时）
                    if current_time - last_send_time > 13:
                        if self.recognizer:
                            try:
                                if audio_buffer:
                                    # 有数据则发送数据
                                    self.recognizer.write(audio_buffer[:SLICE_SIZE])
                                    audio_buffer = audio_buffer[SLICE_SIZE:]
                                else:
                                    # 无数据则发送小量空数据保持连接活跃
                                    self.recognizer.write(b"\x00" * 100)
                                    print("\n长时间无数据发送，发送空数据包保持连接活跃")
                                last_send_time = current_time
                            except Exception as e:
                                print(f"发送音频数据失败: {e}")
                                # 尝试重新创建recognizer
                                if not self.stop_event.is_set() and not self.pause_event.is_set():
                                    self._recreate_recognizer()
                    else:
                        # 当缓冲区达到分片大小时发送，或距离上次发送超过40ms时发送（实时率要求）
                        if len(audio_buffer) >= SLICE_SIZE or (current_time - last_send_time > 0.04 and audio_buffer):
                            if self.recognizer:
                                try:
                                    self.recognizer.write(audio_buffer[:SLICE_SIZE])
                                    last_send_time = current_time
                                    audio_buffer = audio_buffer[SLICE_SIZE:]
                                except Exception as e:
                                    print(f"发送音频数据失败: {e}")
                                    # 尝试重新创建recognizer
                                    if not self.stop_event.is_set() and not self.pause_event.is_set():
                                        self._recreate_recognizer()
                    
                    time.sleep(0.001)
                except OSError as e:
                    # 处理输入溢出，清空缓冲区避免累积
                    if e.errno == -9981:
                        print("警告：音频输入溢出，已重置缓冲区")
                        audio_buffer = b""
                    else:
                        raise e

        except OSError as e:
            # 处理录音设备不可用错误
            print(f"\n录音发生错误: {e}")
            if "Device unavailable" in str(e):
                print("检测到录音设备不可用，尝试延迟后重新初始化...")
                time.sleep(2)  # 延迟2秒后尝试重新初始化
                if not self.stop_event.is_set():
                    print("尝试重新初始化录音设备...")
                    # 重新启动识别
                    self.stop()
                    time.sleep(1)
                    self.start()
        except Exception as e:
            print(f"\n录音发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 安全关闭流（检查流是否已打开）
            if stream is not None:
                try:
                    if stream.is_active():
                        stream.stop_stream()
                    stream.close()
                except Exception:
                    pass  # 忽略关闭流时的错误
            
            try:
                p.terminate()
            except Exception:
                pass  # 忽略终止pyaudio时的错误
            
            # 发送剩余数据
            if len(audio_buffer) > 0 and self.recognizer and not self.pause_event.is_set() and not self.stop_event.is_set():
                try:
                    self.recognizer.write(audio_buffer)
                except Exception:
                    pass  # 忽略发送数据时的错误
            
            if self.recognizer:
                try:
                    self.recognizer.stop()
                except Exception:
                    pass  # 忽略停止识别器时的错误
            
            # 只有在不准备重新启动的情况下才设置is_running为False
            if not hasattr(self, 'stop_event') or self.stop_event.is_set():
                try:
                    self.is_running = False
                except Exception:
                    pass
            
            print("\n录音已停止")

    def _recreate_recognizer(self) -> None:
        """重新创建识别器，用于处理连接断开的情况
        
        返回值:
            None
        """
        start_time = time.time()
        try:
            # 先停止旧的识别器
            if self.recognizer:
                try:
                    self.recognizer.stop()
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|停止旧识别器时发生错误: {e}")
                finally:
                    self.recognizer = None  # 确保旧识别器被释放
            
            
            # 创建新的识别器
            self.recognizer = speech_recognizer.SpeechRecognizer(
                self.appid, self.credential, self.engine_model_type, self.listener)
            
            # 配置识别参数
            self.recognizer.set_filter_modal(1)  # 过滤语气词
            self.recognizer.set_filter_punc(1)   # 过滤标点符号
            self.recognizer.set_filter_dirty(1)  # 过滤脏词
            self.recognizer.set_need_vad(1)      # 启用语音活动检测
            self.recognizer.set_voice_format(1)  # 音频格式为PCM
            self.recognizer.set_word_info(1)     # 返回词级别信息
            self.recognizer.set_convert_num_mode(1)  # 数字转换为中文
            
            # 启动新的识别器
            self.recognizer.start()
            elapsed = (time.time() - start_time) * 1000
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|重新创建识别器|耗时: {elapsed:.2f}ms")
            else:
                print("已重新创建语音识别连接")
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            self.recognizer = None  # 确保识别器为空
            import traceback
            traceback.print_exc()
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|重新创建识别器失败|耗时: {elapsed:.2f}ms|错误: {e}")
            else:
                print(f"重新创建识别器失败: {e}")
    
    def start(self) -> None:
        """开始语音识别
        
        返回值:
            None
        """
        with self.lock:
            if self.is_running:
                # 如果正在运行但处于暂停状态，则恢复
                if self.is_paused:
                    self.resume()
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|启动识别|状态: 识别已在运行中")
                else:
                    print("识别已在运行中")
                return
            
        start_time = time.time()
        # 重置状态
        self.stop_event.clear()
        self.pause_event.clear()
        self.listener.clear_results()
        with self.lock:
            self.is_paused = False
        
        # 创建识别器
        try:
            self._recreate_recognizer()
            
            # 启动麦克风采集线程
            self.capture_thread = threading.Thread(target=self._microphone_audio_capture)
            self.capture_thread.start()
            with self.lock:
                self.is_running = True
            
            elapsed = (time.time() - start_time) * 1000
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|启动识别|耗时: {elapsed:.2f}ms|状态: 语音识别已启动")
            else:
                print("语音识别已启动")
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            if DEBUG_MODE:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|启动识别失败|耗时: {elapsed:.2f}ms|错误: {e}")
            else:
                print(f"启动识别发生错误: {e}")
            with self.lock:
                self.is_running = False

    def stop(self) -> None:
        """停止语音识别
        
        返回值:
            None
        """
        with self.lock:
            if not self.is_running:
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|停止识别|状态: 识别未在运行")
                else:
                    print("识别未在运行中")
                return
            
            # 立即设置状态，防止其他线程干扰
            self.is_running = False
            self.is_paused = False
        
        start_time = time.time()
        # 设置停止标志
        self.stop_event.set()
        self.pause_event.clear()
        
        # 等待采集线程结束
        if self.capture_thread and self.capture_thread.is_alive():
            try:
                self.capture_thread.join(2)  # 等待最长2秒
            except Exception:
                pass
        
        # 停止识别器
        if self.recognizer:
            try:
                self.recognizer.stop()
            except Exception:
                pass  # 忽略停止时的错误
            self.recognizer = None  # 置空识别器，确保下次启动时创建新的
        
        # 重置事件
        self.stop_event.clear()
        
        elapsed = (time.time() - start_time) * 1000
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|停止识别|耗时: {elapsed:.2f}ms|状态: 语音识别已停止")
        else:
            print("语音识别已停止")

    def pause(self) -> None:
        """暂停语音识别（关闭连接，而不是保持连接但不发送数据）
        
        返回值:
            None
        """
        with self.lock:
            if not self.is_running:
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|暂停识别|状态: 识别未在运行中")
                else:
                    print("识别未在运行中，无法暂停")
                return
                
            if self.is_paused:
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|暂停识别|状态: 识别已处于暂停状态")
                else:
                    print("识别已处于暂停状态")
                return
                
        start_time = time.time()
        # 停止当前识别器
        if self.recognizer:
            try:
                self.recognizer.stop()
            except Exception:
                pass  # 忽略停止时的错误
                
        self.pause_event.set()
        with self.lock:
            self.is_paused = True
        
        elapsed = (time.time() - start_time) * 1000
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|暂停识别|耗时: {elapsed:.2f}ms|状态: 语音识别已暂停")
        else:
            print("语音识别已暂停")

    def resume(self) -> None:
        """恢复暂停的语音识别
        
        返回值:
            None
        """
        with self.lock:
            if not self.is_running:
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|恢复识别|状态: 识别未在运行中")
                else:
                    print("识别未在运行中，无法恢复")
                return
                
            if not self.is_paused:
                if DEBUG_MODE:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|恢复识别|状态: 识别未处于暂停状态")
                else:
                    print("识别未处于暂停状态")
                return
                
        start_time = time.time()
        self.pause_event.clear()
        # 恢复时重新创建识别器连接
        self._recreate_recognizer()
        with self.lock:
            self.is_paused = False
        
        elapsed = (time.time() - start_time) * 1000
        if DEBUG_MODE:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|恢复识别|耗时: {elapsed:.2f}ms|状态: 语音识别已恢复")
        else:
            print("语音识别已恢复")

    def get_final_result(self) -> str:
        """获取最终识别结果
        
        返回值:
            str: 最终识别结果字符串
        """
        return self.listener.get_final_result()

    def get_interim_result(self) -> str:
        """获取当前的中间识别结果
        
        返回值:
            str: 中间识别结果字符串
        """
        return self.listener.get_interim_result()

    def is_recognizing(self) -> bool:
        """判断是否正在识别中（未暂停且运行中）
        
        返回值:
            bool: 如果正在识别中返回True，否则返回False
        """
        with self.lock:
            return self.is_running and not self.is_paused

    def clear_results(self) -> None:
        """清除结果缓存，包括中间结果和最终结果
        
        返回值:
            None
        """
        self.listener.clear_results()
        print("结果缓存已清除")


def init(appid: str, secret_id: str, secret_key: str, voice_format: int = 8, sample_rate: int = 16000, 
         hotword_id: str = "", result_type: int = 0, slice_size: int = 960, 
         vad_silence_timeout: int = 10000, vad_pause_timeout: int = 3000, 
         vad_mini_volume: int = 1000, vad_mini_length: int = 500, debug: bool = False,
         vad_threshold: float = 0.7, 
         sentence_callback=None, engine_model_type: str = "16k_zh", 
         interruption_callback=None) -> bool:
    """初始化语音识别
    
    参数:
        appid (str): 腾讯云ASR应用ID
        secret_id (str): 腾讯云API密钥ID
        secret_key (str): 腾讯云API密钥
        voice_format (int): 语音格式，默认8(PCM)
        sample_rate (int): 采样率，默认16000
        hotword_id (str): 热词ID，默认空
        result_type (int): 结果类型，默认0(仅最终结果)
        slice_size (int): 音频分片大小，默认960
        vad_silence_timeout (int): 静音超时时间(毫秒)，默认10000
        vad_pause_timeout (int): 暂停超时时间(毫秒)，默认3000
        vad_mini_volume (int): 最小音量阈值，默认1000
        vad_mini_length (int): 最小语音长度(毫秒)，默认500
        debug (bool): 是否开启调试模式，默认False
        vad_threshold (float): VAD阈值，默认0.7
        sentence_callback (callable): 句子识别完成回调函数
        engine_model_type (str): 引擎模型类型，默认"16k_zh"
        interruption_callback (callable): 打断回调函数
        
    返回值:
        bool: 初始化成功返回True，失败返回False
    """
    global _ai_asr_instance
    
    try:
        # 创建VAD实例
        vad = None
        global ai_vad
        if ai_vad is None:
            try:
                from . import ai_vad
                print("成功导入ai_vad模块")
            except ImportError:
                print("警告: ai_vad模块未找到")
                ai_vad = None
    
        if ai_vad is not None:
            try:
                vad = ai_vad.VADProviderBase.create_vad_instance(
                    vad_mini_volume, vad_mini_length,
                    vad_pause_timeout, vad_silence_timeout,
                    vad_threshold
                )
                print("VAD初始化成功，使用EnergyVADProvider")
            except Exception as e:
                print(f"VAD实例创建失败: {e}")
                vad = None
            
            _ai_asr_instance = TencentSpeechRecognizer(
                appid=appid,
                secret_id=secret_id,
                secret_key=secret_key,
                engine_model_type=engine_model_type,
                sentence_callback=sentence_callback,
                vad=vad,
                interruption_callback=interruption_callback
            )
            print("语音识别初始化成功")
            return True
    except Exception as e:
        print(f"语音识别初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def start() -> None:
    """开始语音识别
    
    返回值:
        None
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化，请先调用 init() 函数")
        return
    _ai_asr_instance.start()


def stop() -> None:
    """停止语音识别
    
    返回值:
        None
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化")
        return
    _ai_asr_instance.stop()


def pause() -> None:
    """暂停语音识别
    
    返回值:
        None
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化")
        return
    _ai_asr_instance.pause()


def resume() -> None:
    """恢复语音识别
    
    返回值:
        None
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化")
        return
    _ai_asr_instance.resume()


def get_final_result() -> str:
    """获取最终识别结果
    
    返回值:
        str: 最终识别结果字符串
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化")
        return ""
    return _ai_asr_instance.get_final_result()


def get_interim_result() -> str:
    """获取当前的中间识别结果
    
    返回值:
        str: 中间识别结果字符串
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化")
        return ""
    return _ai_asr_instance.get_interim_result()


def is_recognizing() -> bool:
    """判断是否正在识别中（未暂停且运行中）
    
    返回值:
        bool: 如果正在识别中返回True，否则返回False
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化")
        return False
    return _ai_asr_instance.is_recognizing()


def clear_results() -> None:
    """清除结果缓存，包括中间结果和最终结果
    
    返回值:
        None
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化")
        return
    _ai_asr_instance.clear_results()


def start_asr_time(seconds: int) -> None:
    """开始语音识别并在指定时间后自动停止
    
    参数:
        seconds (int): 语音识别持续时间（秒）
    
    返回值:
        None
    """
    global _ai_asr_instance
    if _ai_asr_instance is None:
        print("语音识别未初始化，请先调用 init() 函数")
        return
    
    # 开始语音识别
    start()
    
    # 定义定时停止函数
    def stop_after_delay():
        print(f"语音识别将在 {seconds} 秒后自动停止")
        time.sleep(seconds)
        stop()
    
    # 启动定时器线程
    timer_thread = threading.Thread(target=stop_after_delay, daemon=True)
    timer_thread.start()


# 如果直接运行该文件，提供简单的测试功能
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("用法: python ai_asr.py <appid> <secret_id> <secret_key>")
        sys.exit(1)
    
    appid = sys.argv[1]
    secret_id = sys.argv[2]
    secret_key = sys.argv[3]
    
    # 初始化语音识别
    if not init(appid, secret_id, secret_key):
        sys.exit(1)
    
    # 开始识别
    start()
    
    try:
        while True:
            time.sleep(1)
            interim = get_interim_result()
            if interim:
                print(f"中间结果: {interim}")
            
            final = get_final_result()
            if final:
                print(f"最终结果: {final}")
                clear_results()
    except KeyboardInterrupt:
        print("\n停止语音识别...")
        stop()
        sys.exit(0)
