import collections
import numpy as np
from multiprocessing import Process
from myo_bt import Myo
from sklearn.externals import joblib
import time
import threading
import sys


class OnlineFeatureExtractor(Myo):

    def __init__(self, win_size=40, name='', thresh=0.995, n=3):
        Myo.__init__(self)
        
        
        self.win_size = win_size #window size = num of emg datapoints used for each pattern recognition step
        self.thresh=0.995
        self.n=n
        self.transient=False
        
        #self.predictions = collections.deque([False]*self.n, maxlen=self.n)
        #self.initialize_features()
        
        self.state = False #false = rest
        self.count = 0
        self.start_time = 0
        try:
            self.model_flex = joblib.load('../Data/'+name+'_model_binary_'+str(win_size)+'_1.sav')
            self.model_ext = joblib.load('../Data/'+name+'_model_binary_'+str(win_size)+'_2.sav')
        except Exception:
            self.model_flex = joblib.load('../Data/'+name+'_model_binary_1.sav')
            self.model_ext = joblib.load('../Data/'+name+'_model_binary_2.sav')
        


    def on_emg_data(self, emg_data):  
        #print(self.emg_data_queue[-1])
        #print(emg_data[:8])
        #print(emg_data[8:])
        #print('Wooot')
        #print('Waiting:', self.ser.in_waiting)
        self.count+=2
        #self.update_features(emg_data[:8], self.emg_data_queue[0])  
        self.emg_data_queue.append(np.array(emg_data[:8]))
        #self.update_features(emg_data[8:], self.emg_data_queue[0])  
        self.emg_data_queue.append(np.array(emg_data[8:]))
        
         
        self.initialize_features()
        
    def get_emg_data(self):
        return list(self.emg_data_queue)
    
    def initialize_features(self):
        self.mav= np.mean(np.abs(self.emg_data_queue), axis=0)
        self.mean = np.mean(self.emg_data_queue, axis=0)
        self.var = np.var(self.emg_data_queue, axis=0)
        
    
    def update_features(self, x_new, x_old):
        #update features as each emg data comes in
        self.mav= self.mav+((np.abs(x_new)-np.abs(x_old))/self.win_size)
        mean_new = self.mean+((x_new-x_old)/self.win_size)
        self.var = self.var+((x_new-self.mean)**2-(x_old-self.mean)**2)/self.win_size
        self.var = self.var-((mean_new-self.mean)**2) 
        self.mean = mean_new
            
    def get_features(self):
        features = np.concatenate((self.mav, self.var)).reshape(1, -1) 
        return features

    def update_proba(self):
        features = np.concatenate((self.mav, self.var)).reshape(1, -1) 
        
        if self.start_time==0: self.start_time=time.time()
        
        if self.state: #arm is bent
            p = self.model_ext.predict_proba(features)[0][1] #probability of flexion
            print(p)
        else:
            p = self.model_flex.predict_proba(features)[0][1] #probability of extension
        
    
        self.predictions.append(p>self.thresh) 
        
        #print(all(self.predictions), p, self.predictions)
        #print(self.mav)
        #print()
        #print(self.mav-np.mean(np.abs(self.emg_data_queue), axis=1))
        #print(self.var-np.var(self.emg_data_queue, axis=1))
        
        #print()
        #if all(self.predictions):
        #    self.transition()
        #print(all(self.predictions))
    
    
    def transitioning(self):
        command = 'Extend!' if self.state else 'Flex!'
        print(command, '\n')
        print(self.emg_count)
        self.state = not self.state
        input('\nPress enter to continue: ')
        print('\n.........\n')
        print(self.emg_count)
        print('Hold position.')
        self.transition=False
        
    def run_(self, timeout=None):
        
        self.predictions = collections.deque([False]*self.n, maxlen=self.n)
        self.emg_data_queue = collections.deque([np.zeros(8)]*self.win_size, maxlen=self.win_size)
        self.initialize_features()   
        self.transition=False
        while not self.terminate:          
            self.recv_packet(timeout)
            #if self.emg_count%1000==0:  
            if self.transition==False:
                #print(self.ser.in_waiting)
                self.update_proba() 
            if all(self.predictions):
                self.transition=True
                self.predictions = collections.deque([False]*self.n, maxlen=self.n)
                thread = threading.Thread(target=self.transitioning)
                thread.start()

            
            
    
