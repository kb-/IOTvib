# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:08:14 2019

@author: f30154
"""

import numpy as np
from matplotlib import pyplot as plt
from spectralc3 import spectral
import calc

fs=100
t=np.arange(0,10,1/fs)
y=np.sin(2*np.pi*7*t)+0.3*np.sin(2*np.pi*14*t+np.pi/2)
plt.figure()
plt.plot(t,y)
plt.xlabel('t(s)')

plt.figure()

#fs, fftlines, overlap=overlap, win='hann', averaging='exp',nAverage=10
sp = spectral(fs, fs*5, overlap=0.75, win='hanning', averaging='overall',nAverage=10,winParam={"sym":False},detrend='constant')
w1 = sp.w

sp.add(y)
Y, f = sp.get()

plt.semilogy(f,Y)
plt.xlabel('f(Hz)')

sp = spectral(fs, fs*5, overlap=0.75, win='general_cosine', averaging='overall',nAverage=10,winParam={"sym":False,"a":[1, 1.942604, 1.340318, 0.440811, 0.043097]},detrend='constant')
w2 = sp.w
sp.add(y)
Y, f = sp.get()
plt.semilogy(f,Y)
plt.legend()

plt.figure()
plt.plot(w1,lw=0.5)
plt.plot(w2)

print("temporal rms",calc.rms(y))
ecf = sp.getECF()
print("spectral rms",sum((Y*ecf)**2*1/2)**(1/2))
print("NENBW", sp.getNENBW())
print("ECF", ecf)
print("ACF", sp.getACF())
sp.listWindows()