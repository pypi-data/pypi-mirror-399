# coding=utf-8
import time
import struct
from typing import List, Optional
from smartpi import base_driver

        
#马达编码读取 port:连接M端口；
def get_motor_encoder(port:bytes) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x01, 0xBE]           
    motor_str[0]=0XA0+port  
    time.sleep(0.005)     
    response = base_driver.single_operate_sensor(motor_str,0)        
    if response == None:
        return None
    else:
        code_data=response[4:-1]
        code_num=int.from_bytes(code_data, byteorder='big', signed=True)
        return code_num
        
#马达编码置零 port:连接M端口；
def reset_motor_encoder(port:bytes) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x03, 0xBE]           
    motor_str[0]=0XA0+port       
#    response = base_driver.single_operate_sensor(motor_str,0)
    time.sleep(0.005)
    base_driver.write_data(0X01, 0X02, motor_str)
#    if response == None:
#        return None
#    else:
    return 0
        
#马达方向控制 port:连接M端口；dir:0或1
def set_motor_direction(port:bytes,direc:bytes) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x06, 0x71, 0x00, 0xBE]           
    motor_str[0]=0XA0+port
    motor_str[4]=direc
#    response = base_driver.single_operate_sensor(motor_str,0)
    time.sleep(0.005)
    base_driver.write_data(0X01, 0X02, motor_str)
#    if response == None:
#        return None
#    else:
    return 0
        
#马达速度转动 port:连接M端口；speed:-100~100
def set_motor(port:bytes,speed:int) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x02, 0x71, 0x00, 0xBE]           
    motor_str[0]=0XA0+port
    if speed>100:
        m_par=100
    elif speed>=0 and speed<=100:
        m_par=speed        
    elif speed<-100:
        m_par=156
    elif speed<=0 and speed>=-100:
        m_par=256+speed
        
    motor_str[4]=m_par
        
#    response = base_driver.single_operate_sensor(motor_str,0)
    time.sleep(0.005)
    base_driver.write_data(0X01, 0X02, motor_str)
#    if response == None:
#        return None
#    else:
    return 0
        
#马达停止 port:连接M端口；
def set_motor_stop(port:bytes) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x0B, 0xBE]           
    motor_str[0]=0XA0+port
#    response = base_driver.single_operate_sensor(motor_str,0)
    time.sleep(0.005)
    base_driver.write_data(0X01, 0X02, motor_str)
#    if response == None:
#        return None
#    else:
    return 0
        
#马达角度控制 port:连接M端口；speed:-100~100；degree:0~65535
def set_motor_angle(port:bytes,speed:int,degree:int) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x04, 0x81, 0x00, 0x81, 0x00, 0x00, 0xBE]           
    motor_str[0]=0XA0+port
    
    if speed>100:
        m_par=100
    elif speed>=0 and speed<=100:
        m_par=speed        
    elif speed<-100:
        m_par=156
    elif speed<=0 and speed>=-100:
        m_par=256+speed
        
    motor_str[4]=m_par
    motor_str[6]=degree//256
    motor_str[7]=degree%256
#    response = base_driver.single_operate_sensor(motor_str,0)
    time.sleep(0.005)
    base_driver.write_data(0X01, 0X02, motor_str)
#    if response == None:
#        return None
#    else:
    return 0
        
#马达定时转动 port:连接M端口；speed:-100~100；second:1~256
def set_motor_second(port:bytes,speed:int,second:float) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x08, 0x81, 0x00, 0x82, 0x00, 0x00, 0x00, 0x00, 0xBE]           
    motor_str[0]=0XA0+port
    
    if speed>100:
        m_par=100
    elif speed>=0 and speed<=100:
        m_par=speed        
    elif speed<-100:
        m_par=156
    elif speed<=0 and speed>=-100:
        m_par=256+speed
        
    motor_str[4]=m_par    
    
    byte_data = struct.pack('f', second)
    byte_array = list(byte_data)
    
    motor_str[6]=byte_array[0]
    motor_str[7]=byte_array[1]
    motor_str[8]=byte_array[2]
    motor_str[9]=byte_array[3]
    
#    response = base_driver.single_operate_sensor(motor_str,0)
    time.sleep(0.005)
    base_driver.write_data(0X01, 0X02, motor_str)
#    if response == None:
#        return None
#    else:
    return 0

#马达定速转动 port:连接M端口；speed:-100~100
def set_motor_constspeed(port:bytes,speed:int) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x09, 0x71, 0x00, 0xBE]           
    motor_str[0]=0XA0+port
    
    if speed>100:
        m_par=100
    elif speed>=0 and speed<=100:
        m_par=speed        
    elif speed<-100:
        m_par=156
    elif speed<=0 and speed>=-100:
        m_par=256+speed
        
    motor_str[4]=m_par
    
#    response = base_driver.single_operate_sensor(motor_str,0)
    time.sleep(0.005)
    base_driver.write_data(0X01, 0X02, motor_str)
#    if response == None:
#        return None
#    else:
    return 0
        
#马达速度读取 port:连接M端口；
def get_motor_speed(port:bytes) -> Optional[bytes]:
    motor_str=[0xA0, 0x01, 0x10, 0xBE]           
    motor_str[0]=0XA0+port 
    time.sleep(0.005)      
    response = base_driver.single_operate_sensor(motor_str,0)        
    if response == None:
        return None
    else:
        code_data=response[4:-1]
        code_num=int.from_bytes(code_data, byteorder='big', signed=True)
        return code_num   

  

        