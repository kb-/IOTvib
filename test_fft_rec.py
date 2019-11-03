# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:08:14 2019

@author: f30154
"""

import numpy as np
from matplotlib import pyplot as plt
from spectralc1 import spectral
import h5py
    
with h5py.File('C:/Users/Olivier/Downloads/D4.mat', 'r') as file:
    y = list(file['D'])

fs = 3200

y = np.array(y).T

plt.figure()
plt.plot(y)
#plt.plot(t,y)
#plt.xlabel('t(s)')

sp0 = spectral(fs, fs, overlap=0.75, win='hann', averaging='lin',nAverage=50)
#sp1 = spec.spectral(fs, fs*10, overlap=0.75, win='blackman', averaging='lin',nAverage=10)
#sp2 = spec.spectral(fs, fs*10, overlap=0.75, win='flattop', averaging='lin',nAverage=10)
#sp3 = spec.spectral(fs, fs*10, overlap=0.75, win='boxcar', averaging='lin',nAverage=10)

Y0 = []
f = []

i=0
    
def cb():
    global Y0, f, i
    i += 1
    Y0, f = sp0.get()
    print(np.max(Y0[10:]))
    #Y1, f = sp1.get()
    #Y2, f = sp2.get()
    #Y3, f = sp3.get()
#    plt.semilogy(f,Y0)
    #plt.semilogy(f,Y1)
    #plt.semilogy(f,Y2)
    #plt.semilogy(f,Y3)
#    plt.xlabel('f(Hz)')
#    if i==50:
#        plt.figure()
#        plt.semilogy(f,Y0)
#        plt.xlabel('f(Hz)')
    

for s in y:
    sp0.add(s, cb)
#    sp1.add(s)
#    sp2.add(s)
#    sp3.add(s)
plt.figure()
plt.semilogy(f,Y0)
plt.xlabel('f(Hz)')
