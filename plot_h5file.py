import numpy as np
from matplotlib import pyplot as plt
import h5py

def plot():

    file = h5py.File('file.h5','r')
    dsts = file.get('ts')
    
    fs=800
    t=np.arange(0, dsts.shape[1]/fs, 1/fs)
    #y=np.sin(2*np.pi*7*t)+0.3*np.sin(2*np.pi*14*t+np.pi/2)
    plt.plot(t, dsts[()].T)
    plt.xlabel('t(s)')
    file.close()