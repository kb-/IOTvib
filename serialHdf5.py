# -*- coding: utf-8 -*-
#fail, missing data but reads
import threading
import serial
import struct
#import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

port = 'COM9'
baud = 500000
fmt = "<BBIIhhhH"
l_packet = 8

s = serial.Serial(port, baud, timeout=1)

sync = False
l_fmt = struct.calcsize(fmt)

bs=bytearray(l_fmt*2)#sync buffer
#b=bytearray(l_fmt*l_packet)#data buffer
df = pd.DataFrame(data=[],columns=('break','len','t','n','x','y','z','i'))
cnt = 0

def handle_data(b):
    global cnt
    #print(len(b))
#    print(b)
    for i in range(l_packet-1):
        x=struct.unpack_from(fmt,b[i*l_fmt:(i+1)*l_fmt])
        df.loc[cnt] = x
        #print(x)
        cnt+=1
    

def sync_data(bs):
    for i in range(l_fmt):
        #1st sync byte & second sync byte & data length (fmt-sync-length byte)
        if ((bs[i]==0XAA)&(bs[i+l_fmt]==0XAA)&(bs[i+1]==l_fmt-2)):
            return i

def read_from_port(s):
    global sync
    if not sync:
        bs=s.read(l_fmt*2)
        lag = sync_data(bs)
        print(lag)
        s.read(lag)#discard out ofsync data
       
       #check sync
#       b=s.read(36)
#       lag = sync_data(b)
#       print(lag)
        sync = True
       
    while sync:
#        print("sync ok")
        if s.in_waiting > l_packet*l_fmt:
            b=s.read(l_packet*l_fmt)
            handle_data(b)
#        s.close()

thread = threading.Thread(target=read_from_port, args=(s,))
thread.start()