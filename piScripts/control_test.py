# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 20:15:54 2018
@author: ACER ASPIRE X3475
"""
#TODO: add in readable paramters file
#TODO: test window size of 100ms


from online_feature_extractor import OnlineFeatureExtractor
from controller import Controller
import sys
import threading
import time

if __name__ == '__main__':


    name = input('Enter user name: ') 
    try: 
        parameter = int(input('Please enter an integer value > 0 for the control parameter (default=3): '))
    except ValueError:
        parameter = 3
    ft_extractor = OnlineFeatureExtractor()
    ft_extractor.connect_myo()
    
    input('Press enter to start: ')
    sys.stdout.write('\rHold position.')
    controller = Controller(name, n=parameter)
    
    try:
        ft_extractor.initalize()
        listening = threading.Thread(target=ft_extractor.run_)
        listening.start()
        while True:
            features = ft_extractor.get_features()
            controller.update_proba(features)
            time.sleep(0.05)
    except Exception as e:
            print('Keyboard interrupt.')
    finally:
        ft_extractor.terminate=True
        while listening.isAlive():
            pass
        print('Disconnecting.')
        ft_extractor.disconnect()
        