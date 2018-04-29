# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 20:15:54 2018
@author: ACER ASPIRE X3475
"""
#TODO: add in readable paramters file
#TODO: test window size of 100ms


from online_feature_extractor import OnlineFeatureExtractor
import sys
import threading
import time

            


if __name__ == '__main__':


    name = 'Kieran' #input('Enter user name: ') 
    win_size = 40
    parameter = 3
    ft_extractor = OnlineFeatureExtractor(name=name, win_size=win_size, n=parameter)
    ft_extractor.connect_myo()
    
    input('Press enter to start: ')
    sys.stdout.write('\rHold position.')
    #controller = Controller(name, n=parameter, win_size=win_size)
    
    
    
    try:
        ft_extractor.initalize()
        
        ft_extractor.run_()
        #listening = threading.Thread(target=ft_extractor.run_)
        #listening.start()
        #listening.join()
        #while True:
        #    pass
            #ft_extractor.transition
    except KeyboardInterrupt as e:
            print('Keyboard interrupt.')

    finally:
        #ft_extractor.terminate=True
        
        print('Frequency:', ft_extractor.count/(time.time()-ft_extractor.start_time), 'Hz.')
        print('Disconnecting.')
        
        ft_extractor.disconnect()
        
