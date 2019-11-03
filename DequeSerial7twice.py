# -*- coding: utf-8 -*-
#
# get binary data from Arduino, transfer binary data to browser
#ok with 2 gather (connected to 1) :)

import threading
import serial
import struct
import time
import collections
import asyncio
#import datetime
#import random
import websockets
#import struct

#read Arduino param
port = 'COM9'
baud = 500000
fmt = "<bbIIhhhH"
l_packet = 320

ser = serial.Serial(port, baud, timeout=1)
sync = False
l_fmt = struct.calcsize(fmt)
#b=bytearray(l_fmt*l_packet)#data buffer


#send to browser param
datafreq = 3200
l_fmt = struct.calcsize(fmt)
dataready = False
cnt = 0
buffer = collections.deque()

def read_from_port(s,appendData):
    syncB(s, s.read(l_fmt*2))       #sync data with 2 samples
    while True:
        if s.inWaiting() > 5760:
            read_byte = s.read(5760)#read 0.1 s of data
            if read_byte is not None:
                appendData(read_byte)#append element to right of buffer
        time.sleep(0.09)#reduce CPU load
        
#synchronize data stream with sync bytes
def syncB(s, d):
    for i in range(l_fmt):
        #1st sync byte & second sync byte & data length (fmt-sync and length bytes)
        if d[i] == 0XAA & d[i+l_fmt] == 0XAA & d[i+1] == l_fmt-2:
            break #i at break is out of sync data length
    s.read(i)     #discard out of sync data

#websocket
async def useB(websocket, path):
    # start_time = time.time()
    while True:
        try:
            data = buffer.popleft()#pop element from left of buffer (oldest read_byte block)
            await websocket.send(data)
            await asyncio.sleep(0.09)
        except IndexError:  #don't stop if first reads are empty
            continue

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('done')

async def gat():
    await asyncio.gather(s1(5678), s1(5677))
        
async def s1(port):
    return await websockets.serve(useB, "127.0.0.1", port)
    
try:
#    start_server1 = websockets.serve(useB, "127.0.0.1", 5678)
#    start_server2 = websockets.serve(useB, "127.0.0.1", 5678)
    

    thread = threading.Thread(target=read_from_port, args=(ser,buffer.append))
    thread.start()

    asyncio.get_event_loop().run_until_complete(gat())
    asyncio.get_event_loop().run_forever()
    
except KeyboardInterrupt:
    ser.close()