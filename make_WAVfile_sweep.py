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

from speaker_sweep_playback import create_pbk_signals

_, _ , chirp = create_pbk_signals()
