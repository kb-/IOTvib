# -*- coding: utf-8 -*-
#
# get binary data from Arduino, transfer binary data to browser
#ok :)

import threading
import serial
import struct
import time
import collections
import asyncio
import functools
#import datetime
#import random
import websockets
from spectralc import spectral
import numpy as np
#import traceback, sys, code
#import struct

#read Arduino param
port = 'COM9'
baud = 500000     #read fast! don't lose too much CPU cycles reading
l_packet = 320    #0.1 s of data at 3200 Hz

#sensor data
datafreq = 3200
xGain = 0.00376390                      #gain from ADXL345 X axis
fmt = "<bbIIhhhH" #incoming data format: sync byte, size byte, time uint32, count uint 32, xyz int16, spare uint16

fmt2 = "<f"       #outgoing FFT data format

try:
    ser = serial.Serial(port, baud, timeout=1)
except serial.SerialException:
    ser.close()
    raise
    
l_fmt = struct.calcsize(fmt)

l_fmt = struct.calcsize(fmt)

cnt = 0
buffer = collections.deque()            #read/outgoing data buffer
buffer2 = collections.deque()           #spectrum outgoing data buffer

df = 1                                  #FFT resolution (s)
fftlines = datafreq/df
fft_block_size = fftlines*10  #data block for FFT calculation (set larger than FFT lines to allow averaging)

spectrum = spectral(fft_block_size)

def read_from_port(s, appendData, appendData2):
    syncB(s, s.read(l_fmt*2))           #sync data with 2 samples
    while True:
        if s.inWaiting() > 5760:
            read_byte = s.read(5760)    #read 0.1 s of data
            if read_byte is not None:
                appendData(read_byte)   #append element to right of buffer
                appendData2(read_byte)
                
        time.sleep(0.09)                #reduce CPU load
        
#synchronize data stream with sync bytes
def syncB(s, d):
    for i in range(l_fmt):
        #1st sync byte & second sync byte & data length (fmt-sync and length bytes)
        if d[i] == 0XAA & d[i+l_fmt] == 0XAA & d[i+1] == l_fmt-2:
            break                       #i at break is out of sync data length
    s.read(i)                           #discard out of sync data

#websocket
async def useB(websocket, path):
    # start_time = time.time()
    while True:
        try:
            data = buffer.popleft()     #pop element from left of buffer (oldest read_byte block)
            await websocket.send(data)
            await asyncio.sleep(0.09)
        except IndexError:              #don't stop if first reads are empty
            continue

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('done')

def unpackB(b):
    cnt = 0
    #print(len(b))
#    print(b)
    x = np.zeros(l_packet)
    for i in range(l_packet-1):
        d=struct.unpack_from(fmt, b[i*l_fmt:(i+1)*l_fmt])
        x[cnt] = d[4]*xGain             #x axis
#        df.loc[cnt] = x
        #print(x)
        cnt+=1
    return x

def packB(d):           #d is 2d array
    b = []
    for r in d:         #loop on rows
        for e in r:     #loop on elemets in row
            b += struct.pack(fmt2, e)
    return bytearray(b)

#websocket2
async def useBfft(websocket, path, spec):
    # start_time = time.time()
    while True:
        try:
            dataB = buffer2.popleft()   #pop element from left of buffer (oldest read_byte block)
#            data = unpackB(dataB)
            if dataB is not None:
                data = unpackB(dataB)
#                dataBout =  packB(data)
#                
#                await websocket.send(dataBout)

                #TO DO: use a numpy ring buffer,  https://scimusing.wordpress.com/2013/10/25/ring-buffers-in-pythonnumpy/
                isFull = spec.fill_fft_buffer(data)
                if isFull:
                    y = spec.flush_fft_buffer()
                    Y = spec.fft_spectrum(y, datafreq, fftlines, 0.75, 'hann')
                    d = Y[:int(len(Y)/2)]
                    await websocket.send(packB(d)) #return data: spectrum start frame, end frame, spectrum start time, end time,Y
        except IndexError:              #don't stop if first reads are empty
            continue
        await asyncio.sleep(0.09)
#        except:
#            type, value, tb = sys.exc_info()
#            traceback.print_exc()
#            last_frame = lambda tb=tb: last_frame(tb.tb_next) if tb.tb_next else tb
#            frame = last_frame().tb_frame
#            ns = dict(frame.f_globals)
#            ns.update(frame.f_locals)
#            code.interact(local=ns)

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('done')
    
async def serve(port,fn):
    return await websockets.serve(fn, "127.0.0.1", port)   

async def runTogether():
    bound_useBfft = functools.partial(useBfft, spec = spectrum)#pack arguments for useBff because websockets.serve doen't take extra arguments
    await asyncio.gather(serve(5678, useB), serve(5677, bound_useBfft))

try:
    thread = threading.Thread(target=read_from_port, args=(ser,buffer.append,buffer2.append))
    thread.start()

    asyncio.get_event_loop().run_until_complete(runTogether())
    asyncio.get_event_loop().run_forever()
        
except KeyboardInterrupt:
    ser.close()
    