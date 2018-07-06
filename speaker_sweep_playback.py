# -*- coding: utf-8 -*-
""" Mic-Speaker calibration script
Created on Tue Feb 06 15:51:00 2018

Once this script is triggered,
the experimenter is supposed to walk around with the speaker in hand so that
they are visible to the camera while pointing in the general direction of the
speaker.

@author: tbeleyur
"""
import sys
sys.path.append('C:\\Users\\tbeleyur\\Documents\\common\\Python_common\\python_fieldrecorder\\')
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
from  ADC_delay import timealign_channels,save_as_singlewav_timestamped,\
            select_channels
import scipy.io.wavfile as WAV
import sounddevice as sd
import Queue
import time


def create_pbk_signals():
    '''Create the sync, trigger and sweep for playbacks that will create the
    common positions for camera and mic arrays.

    The sweeps are generated between 16-96 KHz, and are 8 ms long
	

    '''
    fs = 192000

    # create the sync signal :
    fps = 25.0 # frames per second
    t_1frame = np.linspace(0,1/fps,int(fs/fps))
    one_frame = signal.square(2*np.pi*fps*t_1frame -np.pi)

    sync_1sec = np.float32(np.tile(one_frame,int(fps)))

    # create the trigger :
    trig_freq = 20*10**3
    t_trig = np.linspace(0,1.0,fs)
    trig_1sec = np.float32(np.cos(2*np.pi*trig_freq*t_trig))


    # create the sweep signal :
    chirp_durn = 0.008
    t_chirp = np.linspace(0,chirp_durn,int(fs*chirp_durn))
    start_freq , end_freq = 16000, 96000

    sweep = signal.chirp(t_chirp, start_freq, t_chirp[-1],end_freq,'hyperbolic')
    sweep *= signal.tukey(sweep.size,0.8)
    sweep = np.float32(sweep)
    sweep *= np.linspace(1,1.125,sweep.size)
    # normalise so values remain between +1/-1
    sweep *= 1/np.abs(np.max(sweep))

    chirp_silence = np.zeros(int(fs/2.0) - sweep.size)
    one_chirp_pbk = np.float32(np.concatenate((chirp_silence,sweep)))
	chirp_pbk = np.tile(one_chirp_pbk, 2)

    return(sync_1sec, trig_1sec, chirp_pbk)


def write_arraytowav(destination_file,recarray,fs=192000):
    '''
    '''
    try:
        WAV.write(destination_file,fs,destination_file)
        print('Saved file to ',destination_file,' successfully!')
    except:
        print('Could not write recording to WAV file...')

sync1s, trig1s, chirp1s = create_pbk_signals()

fs = 192000 ;
block_size = fs;
# prepare output signals into a single array :

output_signals = np.float32(np.zeros((fs,5)))
output_signals[:,0] = sync1s
output_signals[:,1] = trig1s
output_signals[:,2] = sync1s*0.5
output_signals[:,3] = chirp1s*0.25
output_signals[:,4] = chirp1s

output_signals_norec = np.copy(output_signals)
output_signals_norec[:,1] = np.zeros(trig1s.size)

S = sd.Stream(samplerate=fs,blocksize = block_size, device = 56,
                          channels = [24,5] )
S.start()

q = Queue.Queue()


print('playing back now...')

start_time = time.time()

camera_warmuptime = 10
camera_rec_time = 10
camera_warmdown = 5
total_durn = camera_warmuptime + camera_rec_time + camera_warmdown



while time.time()-start_time < total_durn:
    time_sincestart = time.time() - start_time

    if  camera_rec_time+camera_warmuptime > time_sincestart > camera_warmuptime:

        underflow = S.write(output_signals)
        indata, overflow = S.read(fs)
        q.put(indata)

        if underflow:
            raise ValueError('Underflow')
    else :
        underflow = S.write(output_signals_norec)
        if underflow:
            raise ValueError('Underflow')





S.stop()

all_queueparts = []
while not q.empty():
    all_queueparts.append(q.get())

rec = np.concatenate(all_queueparts)
plt.plot(rec[:,0])

plt.figure(2)
plt.specgram(rec[:,0],Fs=192000)

rec_channels = [0,1,2,3,4,5,6,7,12,13,14,15,16,17,18,19]
ch2dev = {'1':range(12),'2':range(12,24)}
sync2dev = {'1':7,'2':19}

allch_aligned = timealign_channels(rec,fs=192000,channels2devices=ch2dev,
                                                     syncch2device=sync2dev,
                                                     with_sync = True)
tristar_channels = select_channels(rec_channels,allch_aligned)
#fname = 'C:\\Users\\tbeleyur\\Documents\\fieldwork_2018\\actrackdata\\wav\\2018-06-22_003\\Mic'
fname = 'C:\\Users\\tbeleyur\\Desktop\\test\\Mic'
save_as_singlewav_timestamped(tristar_channels,192000, file_start=fname)


