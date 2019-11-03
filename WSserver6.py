# -*- coding: utf-8 -*-
#!/usr/bin/env python

# transfer binary data to browser

import asyncio
#import datetime
import random
import websockets
import struct

ndata = 256
datafreq = 3200
fmt = "<f"
l_fmt = struct.calcsize(fmt)
bs=bytearray(l_fmt*ndata)

sendDelay = ndata/datafreq

async def time(websocket, path):
    while True:
        
        for i in range(ndata):
            data = random.random()-0.5
#            print(data)
            struct.pack_into(fmt,bs,l_fmt*i,data)
        
        await websocket.send(bs)
        await asyncio.sleep(sendDelay)

start_server = websockets.serve(time, "127.0.0.1", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()