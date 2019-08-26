# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:08:14 2019

@author: f30154
"""

import numpy as np
from matplotlib import pyplot as plt
from spectralc1 import spectral

fs=1000
t=np.arange(0,50,1/fs)
y=np.sin(2*np.pi*7*t)+0.3*np.sin(2*np.pi*14*t+np.pi/2)
plt.plot(t,y)
plt.xlabel('t(s)')

sp0 = spectral(fs, fs*2, overlap=0.75, win='hann', averaging='exp',nAverage=50)
#sp1 = spec.spectral(fs, fs*10, overlap=0.75, win='blackman', averaging='lin',nAverage=10)
#sp2 = spec.spectral(fs, fs*10, overlap=0.75, win='flattop', averaging='lin',nAverage=10)
#sp3 = spec.spectral(fs, fs*10, overlap=0.75, win='boxcar', averaging='lin',nAverage=10)

    
def cb():
    plt.figure()
    Y0, f = sp0.get()
    print(np.max(Y0[20:]))
    print(np.max(Y0))
    #Y1, f = sp1.get()
    #Y2, f = sp2.get()
    #Y3, f = sp3.get()
#    plt.semilogy(f,Y0)
    #plt.semilogy(f,Y1)
    #plt.semilogy(f,Y2)
    #plt.semilogy(f,Y3)
#    plt.xlabel('f(Hz)')


for s in y:
    sp0.add(s, cb)
#    sp1.add(s)
#    sp2.add(s)
#    sp3.add(s)