#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 17:09:42 2018

@author: Kieran Ricardo
"""

import collections
import myo
import pandas as pd

class MyListener(myo.DeviceListener):

    def __init__(self, name, queue_size=10000):
        self.emg_data_queue = collections.deque(maxlen=queue_size)
        self.recording = False
        self.df = None
        self.label = None
        self.name = name
        self.columns = ['name', 'movement', 'timestamp'] + ['emg'+str(i) for i in range(1,9)]

    def on_connect(self, device, timestamp, firmware_version):
        device.set_stream_emg(myo.StreamEmg.enabled)

    def on_emg_data(self, device, timestamp, emg_data):   
        if self.recording: self.emg_data_queue.append((timestamp, emg_data))

    def get_emg_data(self):
        return list(self.emg_data_queue)
  
    def start_recording(self, label):
        self.label = label
        self.recording = True
    
    def stop_recording(self):
        print('Number of datapoints recorded: ', len(self.emg_data_queue))
        self.recording = False

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
        if self.df == None: return 0
        try:
            df = pd.read_hdf(self.name+'_emg_data.h5', 'data')
            df = pd.concat((df, self.df))
        except FileNotFoundError:
            df = self.df
        df.to_hdf(self.name+'_emg_data.h5', 'data')

#'/Users/harrypotter/Desktop/sdk/myo.framework'
def get_valid_input(allowed_values, user_prompt):
    invalid_input = True  
    user_input = input(user_prompt)
    while invalid_input:       
        if user_input in allowed_values:
            invalid_input = False
        else:
            user_input = input('\nInvalid input. Please try again: ')
    return user_input
        
#TODO: add in progress report

if __name__ == '__main__':

    try:
        myo.init('myo.framework')
        found = True
    except Exception as e:
        pass
      
    user_prompt1 = 'To start recording please enter a number \
1-4 corresponding to one of the following movements/positions: \
\n1. Flexion\n2. Extension\n3. Straight arm\n4. Bent arm\nEnter number: '
    
    user_prompt2 = 'Would you like to record more emg data (y/n): '
    name = input('Enter user name: ') 
    hub = myo.Hub()
    listener = MyListener(name)
    hub.run(200, listener)
    try:  
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
        
    finally:
        hub.shutdown()