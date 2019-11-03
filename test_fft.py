# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:08:14 2019

@author: f30154
"""

import numpy as np
from matplotlib import pyplot as plt
import spectral as spec

fs=100
t=np.arange(0,10,1/fs)
y=np.sin(2*np.pi*7*t)+0.3*np.sin(2*np.pi*14*t+np.pi/2)
plt.plot(t,y)
plt.xlabel('t(s)')

plt.figure()
Y, f, m = spec.fft_spectrum(y, fs, fs*2, 0.75, 'hann')
plt.semilogy(f,Y)
plt.xlabel('f(Hz)')