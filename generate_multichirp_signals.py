# -*- coding: utf-8 -*-
""" Script which generates the required signals for 
the multi-chirp AV playbacks
Created on Fri Jul 20 23:04:25 2018

@author: tbeleyur
"""
import numpy as np 
import scipy.signal as signal 

window_durn = 0.2 # to fit into 4  frames of the camera :
fps = 25.0

fs = 192000
block_durn = 0.2 
block_size = int(fs*block_durn)

t = np.linspace(0,block_durn,block_size)

# make the sync signal 
sync = signal.square(2*np.pi*fps*t -np.pi)

# make the trigger signal 
trigger_freq = 20000.0
trigger = np.cos(2*np.pi*trigger_freq*t)

# save the 0.2 second trigger and sync signal : 
sync_n_trig = np.column_stack((sync, trigger))
np.save('sync_n_trig_0.2ms', sync_n_trig)
