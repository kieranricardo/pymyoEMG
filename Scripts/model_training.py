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

def mav(data):
    return np.mean(abs(data), axis=0)

def emg_filter_highpass(x, order = 4, sRate = 200., lowcut = 10.):
    """ Forward-backward high-pass filtering (IIR butterworth filter) """
    nyq = 0.5 * sRate
    low = lowcut/nyq
    b, a = butter(order, low, btype = 'high', analog=False)    
    return filtfilt(b=b, a=a, x=x, axis=0, method = 'pad', padtype = 'odd', 
                    padlen = np.minimum(3*np.maximum(len(a),len(b)), x.shape[0]-1))



def classifier(action, no_action, dataset):
    
    t1 = dataset[dataset.label==action].timestamp.value_counts().sample(1).index[0]
    t2 = dataset[dataset.label!=action].timestamp.value_counts().sample(1).index[0]
    
    test = dataset[(dataset.timestamp==t1)|(dataset.timestamp==t2)]
    train = dataset[(dataset.timestamp!=t1)&(dataset.timestamp!=t2)]
    
    
    #train = dataset.sample(int(0.8*len(dataset)))
    #test = dataset[~dataset.index.isin(train.index)]
    print(len(dataset), len(train), len(test))
    #print(train.timestamp.value_counts().index)
    #print(test.timestamp.value_counts().index)
    #print(train.label.value_counts())
    #print(test.label.value_counts())
    X = list(train.features)
    y = list(train.label==action)
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5, \
                        hidden_layer_sizes=(15,), random_state=1, verbose=1) 
    clf.fit(X, y) 
    X = list(test.features)
    y_true = list(test.label==action)
    y_pred = clf.predict(X)
    s = accuracy_score(y_true, y_pred)
    joblib.dump(clf, '../Data/'+name+'_model_binary_'+str(action)+'.sav')
    return np.mean(s)


if __name__ == '__main__':
    name = input('Please enter user name: ')
    emg_data = pd.read_hdf('../Data/'+name+'_emg_data.h5', 'data')
    emg_data['emg'] = [np.array(t[3:]) for t in emg_data.itertuples()]  
    
    processed_labels = []
    timestamps = []
    t0 = time.time()
    for t in emg_data.timestamp.value_counts().index:
        current_data = emg_data[emg_data.timestamp==t].copy()
        current_data.emg = emg_filter_highpass(current_data.emg)
        label = current_data.movement[0]
        for i in range(1+len(current_data)-40):
            processed_labels.append(label)
            timestamps.append(t)
            time_slice = current_data.iloc[i:i+40]       
            temp = np.concatenate((mav(time_slice.emg.values), \
                                   np.var(time_slice.emg.values, axis=0)))
            processed_emg.append(temp)
        
    
    t1 = time.time()
    print(t1-t0)
    processed_data = pd.DataFrame()
    processed_data['label'] = processed_labels
    processed_data['features'] = processed_emg
    processed_data['timestamp'] = timestamps
    
    dataset1 = processed_data[processed_data.label.isin([1, 3])] #flexion/straight-arm dataset
    dataset2 = processed_data[processed_data.label.isin([2, 4])] #extension/bent-arm dataset
    
    print(classifier(1, 3, dataset1))
    print(classifier(2, 4, dataset2))
    #processed_data.to_hdf('processed_data.h5', 'data')

        