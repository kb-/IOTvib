# -*- coding: utf-8 -*-
"""
FFT calculation with windowing and averaging
Created on Fri Aug 16 21:43:24 2019

@author: Olivier
"""
import functools
import numpy as np
from scipy import signal as sig
from scipy.fftpack import fft
#import calc
#import pandas as pd

#TO DO: add optional DC removal
#Spectrum and spectral density estimation by the Discrete Fourier
#transform (DFT), including a comprehensive list of window
#functions and some new
#flat-top windows.
#G. Heinzel, A. Rudiger and R. Schilling,
#Max-Planck-Institut fur Gravitationsphysik
#(Albert-Einstein-Institut)
#Teilinstitut Hannover
#February 15, 2002

class spectral:
    """Define and compute spectrum"""
    def __init__(self, fs, nlines,
                 overlap=0.75, win='hann', averaging='overall', nAverage=np.inf, 
                 winParam=None, detrend=False):

        #only allow Scipy windows
        if win not in sig.windows.__all__:
            raise ValueError(f"window {win} doesn't exist. Check https://docs.scipy.org/doc/scipy/reference/signal.windows.html")

        if nAverage == np.inf and averaging == 'exp':
            raise ValueError(f"set nAverage to be able to use exponential averaging")

        self.nl = int(nlines)
        self.databuffer = RingBuffer(self.nl)
        if averaging != 'overall':
            self.fftbuffer = RingBuffer((nAverage, self.nl))           #(navg, nlines)
        self.averaged = np.zeros(self.nl)
        self.summed = np.zeros(self.nl)
        self.fs = fs
        self.o = overlap
        self.win = win
        self.avg = averaging
        self.navg = nAverage
        if winParam is None:
            self.w = getattr(sig, self.win)(self.nl)
        else:
            bound = functools.partial(getattr(sig.windows, self.win), self.nl, **winParam)
            self.w = bound()                   #call existing window methods
        self.m = 0
        self.i = 0
        self.oidx = 0
        self.detrend = detrend
#        self.df = pd.DataFrame(columns = np.arange(1,nlines+1))

    def get(self):
        """Return real side of spectrum and frequencies"""
        b = int(np.ceil(self.nl/2))
        return self.averaged[:b], self.getFreq()[:b]

    def add(self, d, **kwargs):#data, callback
        """Add data to buffer"""
        for j in d:#loop on samples
            cb = kwargs.get('cb', None)
            self.addS(j, cb=cb)

    def addS(self, s, **kwargs):#data, callback
        """Add sample to buffer"""
        self.databuffer.add(np.array([s]))
        #compute spectrum if at requested overlap
        if self.oidx >= self.databuffer.data.shape[0]*(1-self.o) and self.i > self.nl:
#        if self.databuffer.index >= self.databuffer.data.shape[0]*(self.o) == 1:
            self.fft_spectrum(self.databuffer.get())
            self.oidx = 0
            cb = kwargs.get('cb', None)
            if cb is not None:
                cb()
        else:
            self.oidx += 1
        self.i += 1

    def fft_spectrum(self, y):
        """Compute FFT"""
        if self.detrend:
            #linear or constant least squares detrend
            sig.detrend(y, overwrite_data=True, type=self.detrend)

        if self.avg == 'exp':
            self.fft_spectrum_expAvg(y)
        elif self.avg == 'lin':
            self.fft_spectrum_linAvg(y)
        else:
            self.fft_spectrum_overall(y)

    def fft_spectrum_expAvg(self, y):
        """Compute FFT with exponential averaging"""
        self.m += 1
        self.averaged = 1/self.navg*np.abs(fft(y*self.w/np.sum(self.w)))*2 + (1-1/self.navg)*self.averaged

    def fft_spectrum_linAvg(self, y):
        """Compute FFT with linear averaging"""
#        df = self.df.append([y])
#        df.to_hdf('fft_input.h5', 'table', append=True)
        self.fftbuffer.add(np.array([np.abs(fft(y*self.w/np.sum(self.w)))])*2)
        if self.m < self.navg:
            self.m += 1
#        print(self.m)
        Y = np.sum(self.fftbuffer.get(), 0)
        self.averaged = Y/self.m

    def fft_spectrum_overall(self, y):
        """Compute FFT with overall averaging"""
        self.summed = self.summed + np.abs(fft(y*self.w/np.sum(self.w)))
        self.m += 1
        self.averaged = self.summed/self.m*2

    def getFreq(self):
        """Get frequency bands array"""
        return np.arange(0, self.nl)/self.nl*self.fs

    def getAvgCnt(self):
        """Get averaging count"""
        return self.m

    #Derived from:
    #On the Use of Windows for Harmonic Analysis
    #with the Discrete Fourier Transform
    #FREDRIC J. HARRIS
    def getNENBW(self):
        """Get Normalized Equivalent Noise BandWidth"""
        return sum(self.w**2)*self.nl/(sum(self.w))**2

    #Energy Correction Factor of defined window
    #Use to compensate window spectral leakage for spectral RMS calculation
    #spectral rms: sum((Y*ECF)**2*1/2)**(1/2)), with Y amplitude spectrum (positive freq half)
    def getECF(self):
        """Get energy correction factor"""
        return 1/(self.getNENBW())**(1/2)

    def getACF(self):
        """Get Amplitude Correction Factor"""
        return self.nl/sum(self.w)

    @staticmethod
    def listWindows():
        """Get list of supported windows"""
        print(sig.windows.__all__)

#should be faster than deque,
#inspired by: https://scimusing.wordpress.com/2013/10/25/ring-buffers-in-pythonnumpy/
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

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Compute amplitude spectrum with windowing, averaging and overlap')
#    parser.add_argument('--y', metavar='data', required=True,
#                        help='data array')
    parser.add_argument('fs',
                        help='Sampling rate')
    parser.add_argument('nl', metavar='lines',
                        help='number of fft lines (default: sample count)')
    parser.add_argument('--overlap', metavar='overlap',
                        help='overlap 0-1, >0.5 recommanded')
    parser.add_argument('--win', metavar='window',
                        help='hann(general purpose), flattop (very low passband ripple, for calibration) or rectangle (accurate for amplitude but spectral leakage)')
    parser.add_argument('--averaging',
                        help='averaging type: lin,exp,overall (default)')
    parser.add_argument('--nAverage',
                        help='averaging count limit (entire signal if none)')
    parser.add_argument('--winParam',
                        help='dictionary of extra window function named parameters')
    parser.add_argument('--detrend',
                        help='linear detrend (False,"linear","constant")')
    args = parser.parse_args()
    #spectral.fft_spectrum(args.fs, args.nl, overlap=args.overlap, win=args.win, averaging=args.averaging, nAverage=args.nAverage, winParam=args.winParam)
