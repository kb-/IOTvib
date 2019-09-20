# -*- coding: utf-8 -*-
#
# get binary data from Arduino, transfer binary data to browser
#fail TypeError: a coroutine was expected, got <function coroutine.<locals>.coro at 0x0000004AE29D0048>

import threading
import serial
import struct
import time
import collections
import asyncio
import functools
import os
#import datetime
#import random
import websockets
from spectralc import spectral
#import struct

#read Arduino param
port = 'COM9'
baud = 500000
fmt = "<bbIIhhhH"
l_packet = 320

try:
    ser = serial.Serial(port, baud, timeout=1)
except serial.SerialException:
    ser.close()
    raise
    
sync = False
l_fmt = struct.calcsize(fmt)
#b=bytearray(l_fmt*l_packet)#data buffer


#send to browser param
datafreq = 3200
l_fmt = struct.calcsize(fmt)
dataready = False
cnt = 0
buffer = collections.deque()
buffer2 = collections.deque()

fftlines = datafreq*5
spectrum = spectral(fftlines)

def read_from_port(s, appendData, appendData2):
    syncB(s, s.read(l_fmt*2))       #sync data with 2 samples
    while True:
        if s.inWaiting() > 5760:
            read_byte = s.read(5760)#read 0.1 s of data
            if read_byte is not None:
                appendData(read_byte)#append element to right of buffer
                appendData2(read_byte)
                
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
    
#websocket2
async def useBfft(websocket, path, spec):
    # start_time = time.time()
    while True:
        try:
            data = buffer2.popleft()#pop element from left of buffer (oldest read_byte block)
            isFull = spec.fill_fft_buffer(data)
            if isFull:
                y = spec.flush_fft_buffer()
                Y = spec.fft_spectrum(y, datafreq, fftlines, 0.75, 'hann')#TO DO: calculate in thread if asyncio doesn't do it 
                d = Y[:int(len(Y)/2)]
                await websocket.send(d)#return data: spectrum start frame, end frame, spectrum start time, end time,Y
            await asyncio.sleep(0.09)
        except IndexError:  #don't stop if first reads are empty
            continue

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('done')
    
try:
    start_server1 = websockets.serve(useB, "127.0.0.1", 5678)
    bound_useBfft = functools.partial(useBfft, spec = spectrum)
    start_server2 = websockets.serve(bound_useBfft, "127.0.0.1", 5679)

    thread = threading.Thread(target=read_from_port, args=(ser,buffer.append,buffer2.append))
    thread.start()

#    asyncio.run(asyncio.coroutine(runTogether))
    #https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler

#    asyncio.get_event_loop().run_until_complete(asyncio.coroutine(runTogether))#tried to force coroutine, not recognized... 
#    asyncio.get_event_loop().run_forever()
    
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.coroutine(start_server1))
    loop.create_task(asyncio.coroutine(start_server2))
    loop.run_forever()
    
    
except KeyboardInterrupt:
    ser.close()
    