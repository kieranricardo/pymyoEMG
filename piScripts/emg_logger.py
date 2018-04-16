#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 12:49:36 2018

@author: Kieran Ricardo
"""

from myo_bt import Myo
import collections
import pandas as pd
import time
from multiprocessing import Process
import threading

class EMGListener(Myo):
    
    def __init__(self, name, queue_size=10000):
        Myo.__init__(self)        
        self.emg_data_queue = collections.deque(maxlen=queue_size)
        self.recording = False
        self.df = None
        self.label = None
        self.name = name
        self.start_time=None
        
        self.columns = ['movement', 'timestamp'] + ['emg'+str(i) for i in range(1,9)]

    #def on_connect(self, device, timestamp, firmware_version):
    #    device.set_stream_emg(myo.StreamEmg.enabled)

    def on_emg_data(self, emg_data):   
        
        if self.recording: 
            self.emg_data_queue.append((self.start_time, emg_data))

    def get_emg_data(self):
        return list(self.emg_data_queue)
  
    def start_recording(self, label):
        self.label = label
        self.recording = True
        self.start_time = time.time()
    
    def stop_recording(self):
        self.recording = False
        print('Number of datapoints recorded: ', len(self.emg_data_queue))
        print('Frequency: ', len(self.emg_data_queue)/(time.time()-self.start_time))
        self.start_time = None

    def store_data(self):
        data = [(self.label, self.emg_data_queue[0][0])+e[1] for e \
                in self.emg_data_queue]
        temp_df = pd.DataFrame(data)
        temp_df.columns = self.columns
        if self.df is None: self.df = temp_df.copy()
        else: self.df = pd.concat((self.df, temp_df))
        
        
    def clear(self):
        self.label = None
        self.emg_data_queue = collections.deque(maxlen=10000)
    
    def save_data(self):
        if self.df is None: return 0
        try:
            df = pd.read_hdf(self.name+'_emg_data.h5', 'data')
            df = pd.concat((df, self.df))
        except FileNotFoundError:
            df = self.df
        df.to_hdf('../Data/'+self.name+'_emg_data.h5', 'data')


def get_valid_input(allowed_values, user_prompt):
    invalid_input = True  
    user_input = input(user_prompt)
    while invalid_input:       
        if user_input in allowed_values:
            invalid_input = False
        else:
            user_input = input('\nInvalid input. Please try again: ')
    return user_input


if __name__ == '__main__':
    
    user_prompt1 = 'To start recording please enter a number \
1-4 corresponding to one of the following movements/positions: \
\n1. Flexion\n2. Extension\n3. Straight arm\n4. Bent arm\nEnter number: '
    
    user_prompt2 = 'Would you like to record more emg data (y/n): '
    name = input('Enter user name: ') 
    
    listener = EMGListener(name)    
    listener.connect_myo()
    try:
        listener.initalize()
        listening = threading.Thread(target=listener.run_)
        listening.start()
        looping = True
        
        while looping:                                
            movement = get_valid_input(('1', '2', '3', '4'), user_prompt1)
            listener.start_recording(int(movement)) 
            input('Press enter to stop recording.')
            listener.stop_recording()                    
            store = get_valid_input(('y', 'n'), 'Keep data entry (y/n): ')
            if store=='y': listener.store_data()
            listener.clear()
            decision = get_valid_input(('y', 'n'), user_prompt2)
            if decision == 'n': looping = False
        listener.save_data()
        
    except KeyboardInterrupt:
            print('Keyboard interrupt.')
    finally:
        listener.terminate=True
        while listening.isAlive():
            pass
        print('Disconnecting.')
        listener.disconnect()

