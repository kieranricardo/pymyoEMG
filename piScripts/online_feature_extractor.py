import collections
import numpy as np
from multiprocessing import Process
from myo_bt import Myo

class OnlineFeatureExtractor(Myo):

    def __init__(self):
        Myo.__init__(self)
        self.emg_data_queue = collections.deque(np.zeros(40), maxlen=40)
       
        self.mav = np.zeros(8)
        self.var = np.zeros(8)
        self.mean = np.zeros(8)
 

    def on_emg_data(self, emg_data):   
        
        self.update_features(emg_data, self.emg_data_queue[0])        
        self.emg_data_queue.append(np.array(emg_data))

    def get_emg_data(self):
        return list(self.emg_data_queue)
    
    def initialize_features(self):
        
        self.mean = np.mean(self.emg_data_queue, axis=0)
        self.mav = np.mean(np.abs(self.emg_data_queue), axis=0)
        self.var = np.var(self.emg_data_queue, axis=0)
    
    def update_features(self, x_new, x_old):
        self.mav= self.mav+((np.abs(x_new)-np.abs(x_old))/40)
        mean_new = self.mean+((x_new-x_old)/40)
        self.var = self.var+((x_new-self.mean)**2-(x_old-self.mean)**2)/40
        self.var = self.var-((mean_new-self.mean)**2) 
        self.mean = mean_new
            
    def get_features(self):
        features = np.concatenate((self.mav, self.var)).reshape(1, -1) 
        return features


