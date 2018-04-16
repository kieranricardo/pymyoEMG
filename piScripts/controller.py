
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 19:52:55 2018
@author: ACER ASPIRE X3475
"""
import sys
import collections
from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier


class Controller(object):

    def __init__(self, name, n=3, thresh=0.995):
        self.n = n
        self.thresh = thresh
        self.predictions = collections.deque([False]*self.n, maxlen=self.n)
        self.state = False #false = rest
        self.model_flex = joblib.load('../Data/'+name+'_model_binary_1.sav')
        self.model_ext = joblib.load('../Data/'+name+'_model_binary_2.sav')
        
    
    def update_proba(self, features):    
        
        if self.state:
            print(self.model_flex.predict_proba(features)[0][1])
            self.predictions.append(self.model_ext.predict_proba(features)[0][1]>self.thresh)
        else:
            #print(self.model_flex.predict_proba(features)[0][1])
            self.predictions.append(self.model_flex.predict_proba(features)[0][1]>self.thresh)      
        if all(self.predictions):
            self.transition()
        
    def transition(self):
        command = 'Extend!' if self.state else 'Flex!'
        self.state = not self.state
        sys.stdout.flush()
        sys.stdout.write('\r'+command+' '*10)
        #input('\nPress enter once movement is completed: ')
        stop = input('\nWould you like to stop (s) or change parameters (p)? If not simply press enter to continue: ')
        if stop == 's': 
            raise(Exception)
        elif stop == 'p':
            try:
                param = int(input('Please enter an integer value > 0 (default=3): '))
                self.n = param
            except ValueError:
                print('Invalid input. Parameter unchanged.')
        self.predictions = collections.deque([False]*self.n, maxlen=self.n)
        print('\n.........\n')
        sys.stdout.write('\rHold position.')