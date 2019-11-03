# -*- coding: utf-8 -*-
#read ok

import threading
import serial
import struct

port = 'COM9'
baud = 500000
fmt = "<BBIIhhhH"
l_packet = 320

s = serial.Serial(port, baud, timeout=1)

sync = False
l_fmt = struct.calcsize(fmt)

bs=bytearray(l_fmt*2)#sync buffer
#b=bytearray(l_fmt*l_packet)#data buffer

def handle_data(b):
    print(len(b))
    
    x=struct.unpack_from(fmt,b)
    y=struct.unpack_from(fmt,b[l_fmt:])
    print(x)
    print(y)

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
       
    if sync:
        print("sync ok")
        b=s.read(l_packet*l_fmt)
        handle_data(b)
        s.close()

thread = threading.Thread(target=read_from_port, args=(s,))
thread.start()