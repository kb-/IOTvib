# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 21:43:24 2019

@author: Olivier
"""
import numpy as np
from scipy import signal as sig
from scipy.fftpack import fft
#import pandas as pd

#TO DO: handle multiple tracks

class spectral:
    def __init__(self, fs, nlines, overlap=0.75, win='hann', averaging='overall',nAverage=np.inf):

        #only allow Scipy windows
        if win not in sig.windows.__all__:
            raise ValueError(f"window {win} doesn't exist. Check https://docs.scipy.org/doc/scipy/reference/signal.windows.html")

        if nAverage == np.inf and averaging == 'exp':
            raise ValueError(f"set nAverage to be able to use exponential averaging")
           
        self.nl = int(nlines)
        self.databuffer = RingBuffer(self.nl)
        if not averaging == 'overall':
            self.fftbuffer = RingBuffer((nAverage, self.nl))           #(navg, nlines)
        self.averaged = np.zeros(self.nl)
        self.summed = np.zeros(self.nl)
        self.fs = fs
        self.o = overlap
        self.win = win
        self.avg = averaging
        self.navg = nAverage
        self.w = getattr(sig,self.win)(self.nl)                   #call existing window methods
        self.m = 0
        self.i = 0
        self.oidx = 0
#        self.df = pd.DataFrame(columns = np.arange(1,nlines+1))

    #return real side of spectrum and frequencies
    def get(self):
        b = int(np.ceil(self.nl/2))
        return self.averaged[:b], self.getFreq()[:b]

    #add sample to buffer
    def add(self, s, cb):
        self.databuffer.add(np.array([s]))
        #compute spectrum if at requested overlap
        if self.oidx >= self.databuffer.data.shape[0]*(1-self.o) and self.i > self.nl:        
#        if self.databuffer.index >= self.databuffer.data.shape[0]*(self.o) == 1:
            self.fft_spectrum(self.databuffer.get())
            self.oidx = 0
            cb()
        else:
            self.oidx += 1
        self.i += 1
        
    def fft_spectrum(self, y):
        #f = np.arange(0, self.nl)/self.nl*self.fs
        if self.avg == 'exp':
            self.fft_spectrum_expAvg(y)
        elif self.avg == 'lin':
            self.fft_spectrum_linAvg(y)
        else:
            self.fft_spectrum_overall(y)
            
    def fft_spectrum_expAvg(self, y):
        self.m += 1
        self.averaged = 1/self.navg*self.averaged + (1-1/self.navg)*np.abs(fft(y*self.w/np.sum(self.w)))*2
        
    def fft_spectrum_linAvg(self, y):
#        df = self.df.append([y])
#        df.to_hdf('fft_input.h5', 'table', append=True)
        self.fftbuffer.add(np.array([np.abs(fft(y*self.w/np.sum(self.w)))])*2)
        if self.m < self.navg:
            self.m += 1
#        print(self.m)
        Y = np.sum(self.fftbuffer.get(), 0)
        self.averaged = Y/self.m
    
    def fft_spectrum_overall(self, y):               
        self.summed = self.summed + np.abs(fft(y*self.w/np.sum(self.w)))
        self.m += 1
        self.averaged = self.summed/self.m*2
        
    def getFreq(self):
        return np.arange(0, self.nl)/self.nl*self.fs
    
    def getAvgCnt(self):
        return self.m
    
#should be faster than deque, inspired by: https://scimusing.wordpress.com/2013/10/25/ring-buffers-in-pythonnumpy/
class RingBuffer():
    "A nD ring buffer using numpy arrays"
    def __init__(self, length): #(lines, columns)
        self.data = np.zeros(length, dtype='f')
        self.index = 0

    def add(self, x):
        "adds array x to ring buffer"
        x_index = (self.index + np.arange(x.shape[0])) % self.data.shape[0]
        self.data[x_index] = x
        self.index = x_index[-1] + 1

    def get(self):#returns ordonned buffer content (deque doesn't offer a method for that)
        "Returns the first-in-first-out data in the ring buffer"
        idx = (self.index + np.arange(self.data.shape[0])) %self.data.shape[0]
        return self.data[idx]
    
#    def toFIle(self):
#        self.df.to_hdf('fft_input.h5', 'table', append=True)

#class file():
#    def __init__(self, filename, chunkshape):
#        

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Compute amplitude spectrum with windowing, averaging and overlap')
#    parser.add_argument('--y', metavar='data', required=True,
#                        help='data array')
    parser.add_argument('--fs', 
                        help='Sampling rate')
    parser.add_argument('--nl', metavar='lines',
                        help='number of fft lines (default: sample count)')
    parser.add_argument('--o', metavar='overlap',
                        help='overlap 0-1, >0.5 recommanded')
    parser.add_argument('--win', metavar='window',
                        help='hann(general purpose), flattop (very low passband ripple, for calibration) or rectangle (accurate for amplitude but spectral leakage)')
    parser.add_argument('--averaging',
                        help='averaging type: lin,exp,overall (default)')
    parser.add_argument('--nAverage',
                        help='averaging count limit (entire signal if none)')
    args = parser.parse_args()
    spectral.fft_spectrum(y=args.y, fs=args.fs, nl=args.nl, o=args.o, win=args.win, nAverage=args.nAverage) 
        