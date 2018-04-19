# -*- coding: utf-8 -*-
"""Code that playrecs the calibration sounds with the Fireface UC

Created on Fri Jan 19 14:49:37 2018

@author: tbeleyur
"""
import easygui as eg
import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 1000
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as WAV
import datetime as dt

file_folder = 'C:\\Users\\tbeleyur\\Documents\\india_field_season_2018\\calibration\\'

destination_folder = 'C:\\Users\\tbeleyur\\Documents\\india_field_season_2018\\calibration\\calibration_recordings\\2018-01-19\\'


fs, pbksound = WAV.read(file_folder+'multiharmonic_tone.wav')

dev_number = 32 # use sd.query_devices() to get the serial number


play_again = True

i = 0


def save_file():
    timestamp = '_'+dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    rec_name = eg.textbox('please enter the name of the recording : ')
    WAV.write(destination_folder+rec_name+timestamp+'.wav',fs,pbk_rec)
    print('file saved')

while  play_again:
    pbk_rec = sd.playrec(pbksound,samplerate=fs, channels=1,
                         device = dev_number)
    sd.wait()
    plt.figure(i,figsize = (12,8))
    p1 = plt.subplot(211)
    time = np.linspace(0,pbksound.size/float(fs),pbksound.size)
    plt.plot(time,pbk_rec);plt.ylim(-1,1)
    plt.subplot(212,sharex=p1)
    plt.specgram(pbk_rec.flatten(),128,noverlap=100,Fs=fs)

    user_input  = eg.choicebox(msg='Choose next course of action',
                                   choices=['Save','Play again'])

    if user_input == 'Save':
        play_again = False
        save_file()
    elif user_input == 'Play again':
        print('playing again')
    elif user_input is None :
        play_again = False
        print('Stopping playback ')
    i += 1









