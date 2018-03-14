#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 14:09:14 2018

@author: Kieran Ricardo
"""
import collections
import myo
import sys
import numpy as np
from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier
import time
from decimal import Decimal

class realtimeClassifier(myo.DeviceListener):

    def __init__(self, name):
        self.emg_data_queue = collections.deque(maxlen=40)
        self.name = name
        self.model_flex = joblib.load('../Data/'+name+'_model_binary_1.sav')
        self.model_ext = joblib.load('../Data/'+name+'_model_binary_2.sav')
        
        self.mav = None
        self.var = None
        self.mean = None
        self.full = False

    def on_connect(self, device, timestamp, firmware_version):
        device.set_stream_emg(myo.StreamEmg.enabled)

    def on_emg_data(self, device, timestamp, emg_data):   
        if self.full: self.update_features(emg_data, self.emg_data_queue[0])
        elif len(self.emg_data_queue)==40:  self.initialize_features()
        self.emg_data_queue.append(np.array(emg_data))

    def get_emg_data(self):
        return list(self.emg_data_queue)
    
    def initialize_features(self):
        self.full=True
        self.mean = np.mean(self.emg_data_queue, axis=0)
        self.mav = np.mean(np.abs(self.emg_data_queue), axis=0)
        self.var = np.var(self.emg_data_queue, axis=0)
    
    def update_features(self, x_new, x_old):
        self.mav= self.mav+((np.abs(x_new)-np.abs(x_old))/40)
        mean_new = self.mean+((x_new-x_old)/40)
        self.var = self.var+((x_new-self.mean)**2-(x_old-self.mean)**2)/40
        self.var = self.var-((mean_new-self.mean)**2) 
        self.mean = mean_new
            
    def classify(self):
        if not self.var is None:
            features = np.concatenate((self.mav, self.var)).reshape(1, -1)
            probs = self.model_ext.predict(features)[0]
            return probs
        else:
            return -1, -1


if __name__ == '__main__':

    try:
        myo.init()
    except Exception as e:
        pass
    
    name = input('Enter user name: ') 
    hub = myo.Hub()
    listener = realtimeClassifier(name)
    hub.run(200, listener)
    
    try:
        while len(listener.emg_data_queue)<40:
            pass
        space = ' '*50
        while True: 
            sys.stdout.write('\r'+str(listener.classify())+'  ')
            #p0, p1 = listener.classify()
            #sys.stdout.write('\r'+str(Decimal(p0))[:4]+'   '+\
            #                 str(Decimal(p1))[:2])
            sys.stdout.flush()
    except KeyboardInterrupt:
        print('Exiting.')
    
    finally:
        hub.shutdown()
        print('oooh')
    