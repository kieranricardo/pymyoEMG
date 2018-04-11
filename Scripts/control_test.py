# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 20:15:54 2018

@author: ACER ASPIRE X3475
"""
#TODO: add in readable paramters file
#TODO: test window size of 100ms

import myo
from online_feature_extractor import OnlineFeatureExtractor
from controller import Controller
import sys

if __name__ == '__main__':

    try:
        myo.init()
    except Exception as e:
        pass
    
    name = input('Enter user name: ') 
    try: 
        parameter = int(input('Please enter an integer value > 0 for the control parameter (default=3): '))
    except ValueError:
        parameter = 3
    hub = myo.Hub()
    ft_extractor = OnlineFeatureExtractor()
    hub.run(200, ft_extractor)
    input('Press enter to start: ')
    sys.stdout.write('\rHold position.')
    controller = Controller(name, n=parameter)
    
    try:
        while True:
            features = ft_extractor.get_features()
            controller.update_proba(features)
    except Exception as e:
        pass
    finally:
        print('Shutting down the hub.')
        hub.shutdown()