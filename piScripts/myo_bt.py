#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 08:33:03 2018

@author: Kieran Ricardo
"""
import enum
import re
import struct
import sys
import threading
import time
from matplotlib import pyplot as plt
import serial
from serial.tools.list_ports import comports

from utils import pack, unpack, text, multichr, multiord

class Myo(object):
    
    def __init__(self, tty=None):
        self.emg_count = 0
        self.start_time = None
        
        self.emg_char = [0x2b, 0x2e, 0x31, 0x34]
        self.emg_desc = [0x2c, 0x2f, 0x32, 0x35]
        self.packet_starts = [0x00, 0x80, 0x08, 0x88]#[b'\x00', b'\x80', b'\x08', b'\x88']       
        self.terminate = False
        self.emg_arrays = []
        if not tty: tty=self.find_myo()
        self.ser = serial.Serial(port=tty, baudrate=9600, dsrdtr=1)
        
        
    def find_myo(self):
        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]):
                print('using device:', p[0])
                return p[0]
        return None

     
    def initalize(self):
        #subscribe to emg
        #for emg_char in [0x2b, 0x2e, 0x31, 0x34]:
            #self.write_attr(emg_char, b'\x01\00')
        
        #self.write_attr(0x28, b'\x01\00')
        
        self.write_attr(0x19, b'\x01\x03\x02\x00\x00')
        
        
        for attr in self.emg_desc:
            self.write_attr(attr, b'\x01\00')
        
             
        
        #turn emg streaming on
       
    
    def recv_packet(self, payme=False, timeout=None):  
        buff = []
        packet_len = -1
        while len(buff)!=packet_len:
            #print(packet_len, print(len(buff)))
            c = self.ser.read()
            c = ord(c)
            if not buff: 
                if c in self.packet_starts: 
                    buff.append(c)
            elif len(buff)==1: 
                buff.append(c)
                packet_len = 4 + (buff[0] & 0x07) + buff[1]
            else: 
                buff.append(c)             
                      
        payload=bytes(buff[4:])
        if buff[0]==0x80:
            try:
                c, attr, typ = unpack('BHB', payload[:4])       
                if attr in self.emg_char: #==0x27: 
                    if self.emg_count==0: 
                        self.start_time=time.time()
                    self.emg_count+=1   
                    vals = tuple(int(b)-(b//128)*256 for b in buff[9:]) #unpack('8HB', payload[5:]
                    self.on_emg_data(vals[:8])
                    self.on_emg_data(vals[8:])
            except Exception:
                pass
            
        if payme:    
            return buff[:4]+[payload]


    
    def connect_myo(self):
        
        ## stop everything from before
        self.end_scan()
        self.disconnect(0)
        self.disconnect(1)
        self.disconnect(2)
       
        ## start scanning
        print('scanning...')
        self.discover()

        while True:
            packet = self.recv_packet(payme=True)
            payload = packet[-1]
            #print('scan response:', packet)
            print('scanning...')
            if payload.endswith(b'\x06\x42\x48\x12\x4A\x7F\x2C\x48\x47\xB9\xDE\x04\xA9\x01\x00\x06\xD5'):
                addr = list(multiord(payload[2:8]))
                break
        self.end_scan()
        ## connect and wait for status event
        conn_pkt = self.connect(addr)
        self.conn = multiord(conn_pkt[-1])[-1]
        self.wait_event(3, 0)
        ## get firmware version
        fw = self.read_attr(0x17)
        _, _, _, _, v0, v1, v2, v3 = unpack('BHBBHHHH', fw[-1])
        print('Connected!')
        print('Firmware version: %d.%d.%d.%d' % (v0, v1, v2, v3))
        #name = self.read_attr(0x03)
        #print('device name: %s' % name[-1])
        
    
    def send_command(self, cls, cmd, payload=b'', wait_resp=True):
        
        s = pack('4B', 0, len(payload), cls, cmd) + payload
        self.ser.write(s)
        while True:         
            packet = self.recv_packet(payme=True)        
            if packet[0] == 0: return packet
            

    def read_attr(self, attr):
        self.send_command(4, 4, pack('BH', self.conn, attr))
        return self.wait_event(4, 5)

    def write_attr(self, attr, val):
        self.send_command(4, 5, pack('BHB', self.conn, attr, len(val)) + val)
        return self.wait_event(4, 1)


    def run_(self, timeout=None):
        while not self.terminate:
            self.recv_packet(timeout)
    
    def connect(self, addr):
        return self.send_command(6, 3, pack('6sBHHHH', multichr(addr), 0, 6, 6, 64, 0))

    def get_connections(self):
        return self.send_command(0, 6)

    def discover(self):
        return self.send_command(6, 2, b'\x01')

    def end_scan(self):
        return self.send_command(6, 4)

    def disconnect(self, h=None):
        if not h is None:
            return self.send_command(3, 0, pack('B', h))
        elif not self.conn is None:
            return self.send_command(3, 0, pack('B', self.conn))
    
    def wait_event(self, cls, cmd):
        packet_cls = None
        packet_cmd = None
        while not (packet_cls == cls and packet_cmd == cmd):
            packet = self.recv_packet(payme=True)
            packet_cls = packet[2]
            packet_cmd = packet[3]
        return packet
    
    def on_emg_data(self, emg):
        print('old')
        self.emg_arrays.append(emg)
  
    
def plotting(data, sensor):
    plt.figure(1)
    plt.title('Sensor '+str(sensor))
    plt.plot([arr[sensor] for arr in data])#, 'o')
    #plt.plot([arr[sensor]-256*(arr[sensor]//128) for arr in data])
    plt.show()
    
if __name__=='__main__':
    
    myo=Myo()
    myo.connect_myo()
    
    myo.initalize()
    try:
        myo.run_() 
    except KeyboardInterrupt:
        print('Keyboard interrupt.')
    finally:
        print('Disconnecting.')
        myo.disconnect()
        print('EMG streaming rate =', myo.emg_count/(time.time()-myo.start_time), 'Hz.')
    