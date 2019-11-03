# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 21:43:24 2019

@author: Olivier
"""
import numpy as np
from scipy import signal as sig
from scipy.fftpack import fft

#TODO: handle multiple tracks

class spectral:
    def __init__(self, buffersize):
        self.buffer = np.zeros(buffersize)
        self.overflowdata = []
        self.bufferIdx = 0
        
    def fill_fft_buffer(self, d):
        if self.bufferIdx == len(self.buffer):                #buffer already full
            return True
        elif len(d) + self.bufferIdx >= len(self.buffer):#buffer almost full
            l = len(self.buffer[self.bufferIdx:])
            self.buffer[self.bufferIdx:] = d[:l]                #fillremaining space with beginning data
            self.overflowdata = d[l:]                             #store remaining data
            self.bufferIdx += l
            return True
        else:
            self.buffer[self.bufferIdx:self.bufferIdx+len(d)] = d
            self.bufferIdx += len(d)
            return False
            
    def flush_fft_buffer(self):
            self.bufferIdx = 0
            d = self.buffer
            self.buffer[:len(self.overflowdata)] = self.overflowdata
            self.overflowdata = []
            return d

    def fft_spectrum(self, y , fs=1, nl=None, o=0.75, win='hann', nAverage=np.inf):
        n = len(y)
        if nl is None:
            nl = n
        i = 0.
        m = 0
        done = False
        f = np.arange(0, nl)/nl*fs
        Y = np.zeros(nl)

        if win == 'rectangle':
            w = sig.boxcar(nl)
        elif win == 'flattop':
            w = sig.flattop(nl)
        else:
            w = sig.hann(nl)

        while not done:
            a = int(np.floor(i*nl))
            b = int(a+nl)
            Y = np.abs(fft(y[a:b]*w/np.sum(w)))+Y
            i = i+1*(1-o)
            m+=1
            done = b > (n-nl*(1-o)) or m == nAverage
            
        Y = Y/m*2

        return (Y, f, m)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Compute amplitude spectrum with windowing, averaging and overlap')
    parser.add_argument('--y', metavar='data', required=True,
                        help='data array')
    parser.add_argument('--fs', 
                        help='Sampling rate')
    parser.add_argument('--nl', metavar='lines',
                        help='number of fft lines')
    parser.add_argument('--o', metavar='overlap',
                        help='overlap 0-1, >0.5 recommanded')
    parser.add_argument('--win', metavar='window',
                        help='hann(general purpose), flattop (very low passband ripple, for calibration) or rectangle (accurate for amplitude but spectral leakage)')
    parser.add_argument('--nAverage',
                        help='averaging count limit (entire signal if none)')
    args = parser.parse_args()
    spectral.fft_spectrum(y=args.y, fs=args.fs, nl=args.nl, o=args.o, win=args.win, nAverage=args.nAverage) 
        