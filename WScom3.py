#!/usr/bin/env python
#1 https://websockets.readthedocs.io/en/stable/intro.html

# WSS (WS over TLS) client example, with a self-signed certificate

import asyncio
import pathlib
import ssl
import websockets

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
cert = pathlib.Path(__file__).parent / "secret/127.0.0.1-2019-08-10.crt"
ssl_context.load_verify_locations(cert)

async def hello():
    uri = "wss://127.0.0.1:8765"
    async with websockets.connect(
        uri, ssl=ssl_context
    ) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())