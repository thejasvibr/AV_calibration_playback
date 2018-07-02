# -*- coding: utf-8 -*-
""" Script to make the playback sweeps into a WAV file 
Created on Mon Jul 02 10:02:08 2018

@author: tbeleyur
"""


import sys
sys.path.append('C:\\Users\\tbeleyur\\Documents\\common\\Python_common\\AV_calibration_playback\\')
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
import scipy.io.wavfile as WAV

def create_pbk_signals():
    '''Create the sync, trigger and sweep for playbacks that will create the
    common positions for camera and mic arrays.

    The sweeps are generated between 16-96 KHz, and are 6 ms long.

    '''
    fs = 192000

    # create the sweep signal :
    chirp_durn = 0.008
    t_chirp = np.linspace(0,chirp_durn,int(fs*chirp_durn))
    start_freq , end_freq = 16000, 96000

    sweep = signal.chirp(t_chirp, start_freq, t_chirp[-1],end_freq,'hyperbolic')
    sweep *= signal.tukey(sweep.size,0.8)
    sweep = np.float32(sweep)
    # a hack to compensate for the freq response of the speakers
    # amplify the last part of the sweep 
    sweep *= np.linspace(1,1.125,sweep.size)
    # normalise so values remain between -1/1
    sweep *= 1/np.max(sweep)

    return(sweep)

chirp = create_pbk_signals()

WAV.write('chirp.WAV', 192000, chirp)
