#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 20:50:14 2018

@author: harrypotter
"""
from matplotlib import pyplot as plt
import random
import collections
import numpy as np
import myo

#Unsure which plotting style will be the most useful

class RealtimePlotter(myo.DeviceListener):

    def __init__(self, queue_size=400):
        plt.figure()
        plt.ion()
        self.emg_data_queues = [collections.deque(maxlen=queue_size) for i in range(8)]
        self.axes = plt.axes()       
        for ax in self.axes:
            self.ax.set_ylim([0,queue_size])
            self.ax.set_xlim([0,50])

    def on_connect(self, device, timestamp, firmware_version):
        device.set_stream_emg(myo.StreamEmg.enabled)

    def on_emg_data(self, device, timestamp, emg_data):   
        #self.ax.bar(range(1,9), emg_data)
        for i in range(8):
            self.emg_data_queues[i].append(emg_data[i])
            self.axes[i].plot(len(self.emg_data_queues[i]), self.emg_data_queues[i])
        
        plt.pause(1e-9)

if __name__ == '__main__':

    try:
        myo.init()
    except Exception as e:
        pass
    hub = myo.Hub()
    plotter = RealtimePlotter()
    hub.run(200, plotter)
    input('Press enter to stop plotting: ')    

'''
plt.figure()
plt.ion() # set plot to animated
ax=plt.axes() 
plt.hold(False)  


que = collections.deque(np.zeros(40), maxlen=100)
i = 0
try:
    while True: 
        #que.append(random.randint(0,10))
        ax.bar(range(8), np.random.rand(8))
        #ax.set_ylim([0, 10])
        #ax.set_xlim([i, i+40])
        plt.pause(1e-9)
except KeyboardInterrupt: 
    print('Exiting.')
'''