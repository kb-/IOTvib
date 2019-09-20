# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 00:28:51 2019

@author: Olivier
"""
#slow, can't increase much len(d)...

import collections
import threading
import serial
import pandas as pd
import scipy.io

ser = serial.Serial('COM9', 500000)

buffer = collections.deque()
df = pd.DataFrame()
x = []

def readB(s, appendData):
    while True:
        if s.inWaiting() > 8:
            read_byte = s.read(8)
            if read_byte is not None:
                appendData(read_byte)

def useB(d, getData):
    while True: #len(data) < 32:
        try:
            data = getData()
        except IndexError:
            continue
        d += data
        
        print(len(d))
        if len(d) > 10000:
            break

    scipy.io.savemat('f:/tmp/arrdata1.mat', mdict={'arr': d})


read = threading.Thread(target=readB, args=(ser, buffer.append))
use = threading.Thread(target=useB, args=(x, buffer.popleft))

read.start()
use.start()
read.join()
use.join()