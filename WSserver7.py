# -*- coding: utf-8 -*-
#
# get binary data from Arduino, transfer binary data to browser
#seemed ok but probably missing data

import threading
import serial
import struct
import asyncio
#import datetime
#import random
import websockets
#import struct

#read Arduino param
port = 'COM9'
baud = 500000
fmt = "<bbIIhhhH"
l_packet = 256

s = serial.Serial(port, baud, timeout=1)
sync = False
l_fmt = struct.calcsize(fmt)
bs=bytearray(l_fmt*2)#sync buffer
#b=bytearray(l_fmt*l_packet)#data buffer


#send to browser param
datafreq = 3200
l_fmt = struct.calcsize(fmt)
bs=bytearray(l_fmt*l_packet)
dataready = False
cnt = 0


def handle_data(b):
    global dataready
    global bs
    bs[:] = b
    dataready = True #allows websocket send

def sync_data(bs):
    for i in range(l_fmt):
        #1st sync byte & second sync byte & data length (fmt-sync-length byte)
        if ((bs[i]==0XAA)&(bs[i+l_fmt]==0XAA)&(bs[i+1]==l_fmt-2)):
            return i

def read_from_port(s):
    global sync
    global cnt
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
        print("sync ok")
       
    while sync:
        cnt+= 1
        print(cnt)
        b=s.read(l_packet*l_fmt)
        handle_data(b)
    # s.close()

#websocket
async def time(websocket, path):
    global dataready
    global cnt
    global bs
    while True:
#        print(cnt, dataready)
        if dataready: #if received data from Arduino
            print(cnt)
            dataready = False
            await websocket.send(bs)
            await asyncio.sleep(0.001)
        
try:
    start_server = websockets.serve(time, "127.0.0.1", 5678)

    thread = threading.Thread(target=read_from_port, args=(s,))
    thread.start()

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    
except KeyboardInterrupt:
    s.close()