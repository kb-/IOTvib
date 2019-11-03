#!/usr/bin/env python

# fail

import asyncio
import collections
import threading
import time
import websockets
import scipy.io
import pdb

buffer = collections.deque()
x = []
complete = False

async def readB():
    global complete
    uri = "ws://127.0.0.1:5678"
    try:
        async with websockets.connect(uri) as websocket:
            while not complete:
                d = await websocket.recv()
                if d is not None:
                    await buffer.append(d)
                    await asyncio.sleep(0.09)
    except websockets.ConnectionClosed:
        print('complete readB')
        complete = True

def useB(data, pop):
    print('useB')
    global complete
    while True:
        try:
            d = pop()
            if d is not None:
                data += d
#            print(len(d))
#            pdb.set_trace()
            continue
        except IndexError:              #don't stop if first reads are empty
            print('d empty')
            continue
        time.sleep(0.09)
        if complete:
            print('complete useB')
            break
    print('done')
    pdb.set_trace()
    scipy.io.savemat('f:/tmp/arrdata3.mat', mdict={'arr': data})

thread = threading.Thread(target=useB, args=(x, buffer.popleft))
thread.start()

asyncio.get_event_loop().run_until_complete(readB())
