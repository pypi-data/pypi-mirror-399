# -*- coding: utf-8 -*-
import sys
import os
import time
import numpy as np

class VADProviderBase:
    """VAD provider base class"""
    @staticmethod
    def create_vad_instance(
        vad_mini_volume=1000, 
        vad_mini_length=500,
        vad_pause_timeout=3000, 
        vad_silence_timeout=10000,
        threshold=0.02
    ):
        """Factory method to create VAD instance - always returns EnergyVADProvider"""
        # 忽略vad_mini_volume, vad_mini_length, vad_silence_timeout参数
        # 将vad_pause_timeout作为min_silence_duration_ms传递
        return EnergyVADProvider(
            threshold=threshold, 
            min_silence_duration_ms=vad_pause_timeout
        )

class EnergyVADProvider(VADProviderBase):
    """Audio energy-based VAD provider"""
    def __init__(self, threshold=0.02, min_silence_duration_ms=300):
        print(f"Initializing EnergyVAD: threshold={threshold}, min_silence_duration_ms={min_silence_duration_ms}")
        # 初始化VAD配置，使用默认值作为备选
        self.vad_threshold = float(threshold) if threshold else 0.02
        self.silence_threshold_ms = int(min_silence_duration_ms) if min_silence_duration_ms else 300
        print("EnergyVAD initialized successfully")
    
    def is_vad(self, conn, audio_data):
        """使用音频能量检测语音活动"""
        try:
            # 确保conn对象有必要的属性
            if not hasattr(conn, 'client_audio_buffer'):
                conn.client_audio_buffer = []
            if not hasattr(conn, 'client_have_voice'):
                conn.client_have_voice = False
            if not hasattr(conn, 'client_have_voice_last_time'):
                conn.client_have_voice_last_time = 0
            if not hasattr(conn, 'client_voice_stop'):
                conn.client_voice_stop = False
            
            # 将新数据加入缓冲区
            conn.client_audio_buffer.extend(audio_data)
            
            # 处理缓冲区中的数据
            client_have_voice = False
            # 对于能量检测，我们可以使用较小的块大小，例如256采样点
            while len(conn.client_audio_buffer) >= 256 * 2:
                # 提取前256个采样点（512字节）
                chunk = bytes(conn.client_audio_buffer[:256 * 2])
                conn.client_audio_buffer = conn.client_audio_buffer[256 * 2:]
                
                # 计算能量
                audio_int16 = np.frombuffer(chunk, dtype=np.int16)
                energy = np.abs(audio_int16).mean()
                
                client_have_voice = energy > self.vad_threshold
                
                # 更新VAD状态
                if client_have_voice:
                    conn.client_have_voice = True
                    conn.client_have_voice_last_time = time.time() * 1000
                    conn.client_voice_stop = False
                elif conn.client_have_voice:
                    # 检查静默时间
                    stop_duration = time.time() * 1000 - conn.client_have_voice_last_time
                    if stop_duration >= self.silence_threshold_ms:
                        conn.client_have_voice = False
                        conn.client_voice_stop = True
            
            return client_have_voice
        except Exception as e:
            print(f"能量检测出错: {e}")
            return False
    
    def reset_states(self):
        """重置VAD状态"""
        pass  # 状态现在存储在conn对象中，不需要在这里重置