# -*- coding: utf-8 -*-
#!/usr/bin/env python

# transfer binary data to browser ok

import asyncio
#import datetime
import random
import websockets
import struct

fmt = "<f"
bs=bytearray(4)

async def time(websocket, path):
    while True:
        data = random.random()-0.5
        print(data)
        struct.pack_into(fmt,bs,0,data)
        await websocket.send(bs)
        await asyncio.sleep(1)

start_server = websockets.serve(time, "127.0.0.1", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()