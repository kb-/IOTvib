# -*- coding: utf-8 -*-
#
# get binary data from Arduino, transfer binary data to browser
#fail

import threading
import _thread as thread
import serial
import struct
import time
import collections
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
        self.url = 'ws://172.0.0.1:'+port
        
    def start_websocket(self, run_in_background=False):
#        ping_interval = 60
#        ping_timeout = 10
        self.websocket = websocket.WebSocketApp(self.url,
    #                                            header={'Authorization: Bearer' + self.access_token},
    #                                            on_data=self._on_data,
    #                                            on_error=self._on_error,
    #                                            on_close=self._on_close,
                                                on_open=self._on_open)
        if run_in_background is True:
            self.ws_thread = threading.Thread(target=self.websocket.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
        else:
#            self.websocket.run_forever(ping_interval=ping_interval, ping_timeout=ping_timeout)
            self.websocket.run_forever()
    
    def _on_open (self, ws):
        if self.on_open:
            self.on_open(ws)
            
    def set_on_open(self, event_handler):
        self.on_open = event_handler


def useB(websocket, path):
    # start_time = time.time()
    def run(websocket):
        print(killed)
        while not killed:
            try:
                data = buffer.popleft()#pop element from left of buffer (oldest read_byte block)
                websocket.send(data)
                time.sleep(0.09)
            except IndexError:  #don't stop if first reads are empty
                continue
    thread.start_new_thread(run, ())

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('done')
        
try:
#    start_server = websockets.serve(useB, "127.0.0.1", 5678)
    killed = False
    ws = WS()
    ws.set_on_open(useB)
    ws.start_websocket(True)#/True: fail

#    thread = threading.Thread(target=read_from_port, args=(ser,buffer.append))
#    thread.start()

#    asyncio.get_event_loop().run_until_complete(start_server)
#    asyncio.get_event_loop().run_forever()
    
except KeyboardInterrupt:
    ser.close()
    killed = True