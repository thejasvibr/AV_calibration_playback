# -*- coding: utf-8 -*-
""" Script to execute the multi-chirp series 
Created on Fri Jul 20 23:05:52 2018

@author: tbeleyur
"""
import sys
sys.path.append('C:\\Users\\tbeleyur\\Documents\\common\\Python_common\\python_fieldrecorder\\')
import datetime as dt
import numpy as np
import scipy.signal as signal
from  ADC_delay import save_as_singlewav_timestamped,\
            select_channels, write_wavfile
from fieldrecorder import fieldrecorder
import scipy.io.wavfile as WAV
import sounddevice as sd
import Queue
import time

# load the multichip np.array , each 0.2 ms silence+chirp is one row
multi_chirp_series = np.load('US_9chirp_series_0.2msgaps_hf_hackcompensated.npy')
num_rows = multi_chirp_series.shape[0]
reduced_numrows = num_rows - 8

sync_n_trig = np.load('sync_n_trig_0.2ms.npy')

# create the multichannel output when there are no playbacks and when there
# is no recording happening and when there is reocording happening 
fs = 192000
block_size =  multi_chirp_series.shape[1]
camrec_output = np.zeros((block_size,5), dtype=np.float32)
norec_output = np.zeros((block_size,5), dtype=np.float32)

camrec_output[:,0] = sync_n_trig[:,0]
camrec_output[:,1] = sync_n_trig[:,1]
camrec_output[:,2] = sync_n_trig[:,0]*0.25


norec_output[:,0] = sync_n_trig[:,0]


S = sd.Stream(samplerate=fs,blocksize = block_size, device = 64,
                          channels = [28,5] )
S.start()

q = Queue.Queue()


start_time = time.time()

camera_warmuptime = 10
camera_rec_time = 60
camera_warmdown = 1
total_durn = camera_warmuptime + camera_rec_time + camera_warmdown


i = 0
y = []
while time.time()-start_time < total_durn:
    time_sincestart = time.time() - start_time
    
    if  camera_rec_time+camera_warmuptime > time_sincestart > camera_warmuptime:
        chirp_index = np.remainder(i, reduced_numrows)
        y.append([chirp_index,i])
        camrec_output[:,3] = multi_chirp_series[chirp_index,:]*0.15
        camrec_output[:,4] = multi_chirp_series[chirp_index,:]

        underflow = S.write(camrec_output)
        indata, overflow = S.read(block_size)
        q.put(indata)
        i += 1 
        

        if underflow:
            raise ValueError('Underflow')
        
        
    else :
        underflow = S.write(norec_output)
        if underflow:
            raise ValueError('Underflow')


S.stop()

all_queueparts = []
while not q.empty():
    all_queueparts.append(q.get())

all_chrec = np.concatenate(all_queueparts)
recording_channels = range(28)
only_rec_ch = select_channels(recording_channels, all_chrec)
fname = 'C:\\Users\\tbeleyur\\Documents\\fieldwork_2018_002\\actrackdata\\wav\\2018-08-19_003\\SPKRPLAYBACK_multichirp_'
timenow = dt.datetime.now()
timestamp = timenow.strftime('%Y-%m-%d_%H-%M-%S')
file_ending = timestamp+'.WAV'
write_wavfile(only_rec_ch, fs,fname+file_ending)





