#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 20:50:14 2018

@author: Kieran Ricardo
"""

import matplotlib.pyplot as plt
#import random
import collections
import numpy as np
import myo



class EMGListener(myo.DeviceListener):

    def __init__(self, queue_size=800): 
        self.emg_data_queues = [collections.deque(np.zeros(queue_size), maxlen=queue_size) for i in range(8)]

    def on_connect(self, device, timestamp, firmware_version):
        device.set_stream_emg(myo.StreamEmg.enabled)

    def on_emg_data(self, device, timestamp, emg_data):   
        for i in range(8):
            self.emg_data_queues[i].append(emg_data[i])
    
    def get_emg(self):
        return self.emg_data_queues



if __name__ == '__main__':

    try:
        myo.init()
    except Exception as e:
        pass
    plt.figure()
    plt.ion()
    plt.hold(False) 
    f, axarr = plt.subplots(4, sharex=True)
    for ax in axarr:
        ax.set_ylim([-50,50])
    lines = [axarr[i].plot(range(800), np.zeros(800))[0] for i in range(4)]
    f.canvas.draw()
    f.canvas.flush_events()
    
    try:
        
        hub = myo.Hub()
        listener = EMGListener()
        hub.run(200, listener)
        
        try:
            while True: 
                emg = listener.get_emg()
                for i in range(4): 
                    lines[i].set_ydata(emg[i])
                    axarr[i].set_ylim([-50,50])
                    axarr[i].draw_artist(axarr[i].patch)
                    axarr[i].draw_artist(lines[i])
                #plt.pause(1e-9)
                #f.canvas.update()
                f.canvas.flush_events()
        except KeyboardInterrupt: 
            print('Exiting.')
    finally:
        print('Shutting down hub.')
        hub.shutdown()


'''

plt.ion()
plt.hold(False) 
f, axarr = plt.subplots(8, sharex=True)
for ax in axarr:
    ax.set_ylim([0,11])
queues = [collections.deque(np.zeros(40), maxlen=40) for i in range(8)]
lines = [axarr[i].plot(range(40), queues[i])[0] for i in range(8)]
f.canvas.draw()
f.canvas.flush_events()
i = 0
try:
    while True: 
        for i in range(8): 
            queues[i].append(random.randint(0,10))            
            lines[i].set_ydata(queues[i])
            axarr[i].set_ylim([0,11])
            axarr[i].draw_artist(axarr[i].patch)
            axarr[i].draw_artist(lines[i])
        #f.canvas.update()
        f.canvas.flush_events()
        #plt.pause(1e-9)
except KeyboardInterrupt: 
    print('Exiting.')

'''