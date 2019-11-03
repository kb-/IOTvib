# -*- coding: utf-8 -*-
#
# get binary data from Arduino, transfer binary data to browser
#fail in thread mode (thread not running)

import threading
import serial
import struct
import time
import collections
import asyncio
import requests
#import datetime
#import random
import websocket
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

#websocket inspired by https://github.com/upstox/upstox-python/blob/master/upstox_api/api.py
class WS:
    def __init__(self, port='5678'):
        self.url = 'ws://172.0.0.1:'+port+'/'
        self.connected = False
        self.ws = None
        self.mainMutex = threading.Lock()
        self.mainThread = None
        self.callback = None
        self.trace = False
        
    def connect(self):
        if(not self.isConnected()):
            self.ws = websocket.WebSocketApp(self.url,
#                                             on_message=self.onRecieve,
                                             on_error=self.onError,
                                             on_close=self.onClose)

            self.ws.on_open = self.onOpen
            # Start the actual connection
            self.mainThread = threading.Thread(
                target=self.ws.run_forever, args=())
            self.mainThread.start()
        else:
            print("Attempting to connect but already connected.")

    def onOpen(self):
        print("Websocket connection opened.")
        self.connected = True
        useB(self.ws)
        
    def onError(self, error):
        """When websocket recieves an error it ends up here"""
        print(error)
        
    def onClose(self):
        """After closing websocket"""
        print("Websocket connection closed.")
        self.connected = False
        
    def isConnected(self):
        """Checks if we're connected to the websocket"""
        # self.mainMutex.acquire()
        isCon = self.connected
        # self.mainMutex.release()
        return isCon

def useB(websocket):
    # start_time = time.time()
    print(killed)
    while not killed:
        try:
            data = buffer.popleft()#pop element from left of buffer (oldest read_byte block)
            websocket.send(data)
            time.sleep(0.09)
        except IndexError:  #don't stop if first reads are empty
            continue

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('done')
        
try:
#    start_server = websockets.serve(useB, "127.0.0.1", 5678)
    killed = False
    ws = WS()
    ws.connect()

    thread = threading.Thread(target=read_from_port, args=(ser,buffer.append))
    thread.start()

#    asyncio.get_event_loop().run_until_complete(start_server)
#    asyncio.get_event_loop().run_forever()
    
except KeyboardInterrupt:
    ser.close()
    killed = True