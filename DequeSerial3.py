# -*- coding: utf-8 -*-
#read binary stream from serial port. Sync and save to Matlab file.
"""
Created on Wed Aug 14 00:28:51 2019

@author: Olivier
"""

import collections
import threading
import time
import struct
import serial
import pandas as pd
import scipy.io

ser = serial.Serial('COM9', 500000)
fmt = "<BBIIhhhH" #binary data structure format (1 sample)

l_fmt = struct.calcsize(fmt) #sample size
buffer = collections.deque()
df = pd.DataFrame()
x = []

#read binary data from serial port to buffer
def readB(s, appendData):
    syncB(s, s.read(l_fmt*2))       #sync data with 2 samples
    while True:
        if s.inWaiting() > 5760:
            read_byte = s.read(5760)#read 0.1 s of data
            if read_byte is not None:
                appendData(read_byte)#append element to right of buffer
        time.sleep(0.09)#reduce CPU load

#use binary data in buffer (without blocking reads)
def useB(d, getData):
    start_time = time.time()
    while True:
        try:
            data = getData()#pop element from left of buffer (oldest read_byte block)
            d += data
            time.sleep(0.09)#reduce CPU load
        except IndexError:  #don't stop if first reads are empty
            continue
#        print(len(d))
        if len(d) > 3200*10*18:
            break

    print("--- %s seconds ---" % (time.time() - start_time))
    print('done')
    scipy.io.savemat('f:/tmp/arrdata2.mat', mdict={'arr': d})

#synchronize data stream with sync bytes
def syncB(s, d):
    for i in range(l_fmt):
        #1st sync byte & second sync byte & data length (fmt-sync and length bytes)
        if d[i] == 0XAA & d[i+l_fmt] == 0XAA & d[i+1] == l_fmt-2:
            break #i at break is out of sync data length
    s.read(i)     #discard out of sync data

#assign functions to threads
read = threading.Thread(target=readB, args=(ser, buffer.append))
use = threading.Thread(target=useB, args=(x, buffer.popleft))

read.start()
use.start()
read.join()
use.join()
