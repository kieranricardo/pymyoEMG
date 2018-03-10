#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 21:43:18 2018

@author: harrypotter
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 13:32:44 2018


@author: Kieran Ricardo
"""
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
from scipy.signal import butter, filtfilt, lfilter
import time

def mav(xs):
    return np.mean([abs(x) for x in xs], axis=0)

def emg_filter_bandpass(x, order = 4, sRate = 200., lowcut = 10.):
    """ Forward-backward band-pass filtering (IIR butterworth filter) """
    nyq = 0.5 * sRate
    low = lowcut/nyq
    b, a = butter(order, low, btype = 'high', analog=False)    
    return filtfilt(b=b, a=a, x=x, axis=0, method = 'pad', padtype = 'odd', 
                    padlen = np.minimum(3*np.maximum(len(a),len(b)), x.shape[0]-1))

def update(mean_old, mean_abs, var, x0, x1, n):
    '''
    Updates features using the values entering and leaving the window.
    '''
     

def classifier(action, no_action, dataset):
    #t1 and t2 are timestamps of a recording of an action and a rest state respectively
    t1 = dataset[dataset.label==action].timestamp.value_counts().sample(1).index[0]
    t2 = dataset[dataset.label!=action].timestamp.value_counts().sample(1).index[0]
    #t1 and t2 are used for test data. This is done so that one
    #entire recording of each movement is reserved as a test set.
    
    test = dataset[(dataset.timestamp==t1)|(dataset.timestamp==t2)]
    train = dataset[(dataset.timestamp!=t1)&(dataset.timestamp!=t2)]
    
    print(len(dataset), len(train), len(test))

    X = list(train.feature)
    y = list(train.label==action)
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5, early_stopping=True, \
                        hidden_layer_sizes=(15,), random_state=1) 
    clf.fit(X, y) 
    X = list(test.feature)
    y_true = list(test.label==action)
    y_pred = clf.predict(X)
    s = accuracy_score(y_true, y_pred)
    #saves the coefficents of the classifier for online classification
    joblib.dump(clf, '../Data/'+name+'_model_binary_'+str(action)+'.sav')
    return np.mean(s)



if __name__ == '__main__':
    name = input('Please enter user name: ')
    emg_data = pd.read_hdf('../Data/'+name+'_emg_data.h5', 'data')
    
    #stores each emg reading as an (8,) ndarray, the data logger will be updated in 
    #the future to store data in this format
    emg_data['emg'] = [np.array(t[3:]) for t in emg_data.itertuples()]
    
    features = [] #empty list to hold the emg features
    labels = [] #empty list to hold corresponding labels
    timestamps = [] #empty list to hold  timetamp of first measurement

    t0 = time.time()
    
    #each datapoint in a recording is paired with the timestamp of the start of the recording
    #timestamp is used as a key to acess different recordings 
    for t in emg_data.timestamp.value_counts().index:   
        current_data = emg_data[emg_data.timestamp==t]#.copy()       
        current_data.emg = emg_filter_bandpass(current_data.emg)
        label = current_data.movement[0]
        current_data = current_data.emg
        
        mean_abs = mav(current_data.iloc[:40].values) #mean absolute value
        mean = np.mean(current_data.iloc[:40].values, axis=0)
        var = np.var(current_data.iloc[:40].values, axis=0)#[(x-m)**2 for x in current_data.iloc[:40]], axis=0)
        
        features.append(np.concatenate((mean,var)))

        for i in range(len(current_data)-40):
            #optimized, updates mav and var using minimal operations
            #x0 = datapoint being removed from the window
            #x1 = datapoint being added to the window
            x0 = current_data.iloc[i]
            x1 = current_data.iloc[i+40]
            #updates mean, mav and var
            mean, mean_abs, var = update(mean, mean_abs, var, x0, x1, 40) 
            features.append(np.concatenate((mean_abs,var)))
        labels.extend([label]*(i+2))
        timestamps.extend([t]*(i+2))
    t1 = time.time()
    print(t1-t0)
    processed_data = pd.DataFrame()
    processed_data['label'] = labels
    processed_data['feature'] = features
    processed_data['timestamp'] = timestamps
    
    
    dataset1 = processed_data[processed_data.label.isin([1, 3])] #straight arm/flexion data
    dataset2 = processed_data[processed_data.label.isin([2, 4])] #bent arm/extension data
    
    #2 binary classifiers are used because for our purposes we only need to distuingish between:
        #flexion and bent arm when the arm is bent
        #extension and straigh arm when the arm is straight
    #don't need to distinguish between extension and flexion, extension and straight etc.

    print(classifier(1, 3, dataset1))
    print(classifier(2, 4, dataset2))
    #processed_data.to_hdf('processed_data.h5', 'data')

        