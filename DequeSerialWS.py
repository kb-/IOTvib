# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 00:28:51 2019

@author: Olivier
"""

import collections
import threading
import serial
import pandas as pd
import scipy.io
import time
import websockets

ser = serial.Serial('COM9', 500000)

buffer = collections.deque()
df = pd.DataFrame()
x = []

def readB(s, appendData):
    while True:
        if s.inWaiting() > 5760:
            read_byte = s.read(5760)
            if read_byte is not None:
                appendData(read_byte)

def useB(d, getData):
    start_time = time.time()
    while True: #len(data) < 32:
        try:
            data = getData()
            d += data
        except IndexError:
            continue
        
#        print(len(d))
        if len(d) > 3200*10*18:
            break
    
    print("--- %s seconds ---" % (time.time() - start_time))
    print('done')
    scipy.io.savemat('f:/tmp/arrdata2.mat', mdict={'arr': d})
    


read = threading.Thread(target=readB, args=(ser, buffer.append))
use = threading.Thread(target=useB, args=(x, buffer.popleft))

read.start()
use.start()
read.join()
use.join()