#!/usr/bin/env python
#1 https://websockets.readthedocs.io/en/stable/intro.html

# WSS (WS over TLS) server example, with a self-signed certificate
#fail
import asyncio
import pathlib
import ssl
import websockets

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
cert = pathlib.Path(__file__).parent / "secret/127.0.0.1-2019-08-10.crt"
key = pathlib.Path(__file__).parent / "secret/127.0.0.1-2019-08-10.key"


ssl_context.load_cert_chain(cert,key)

start_server = websockets.serve(
    hello, "localhost", 8765, ssl=ssl_context
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
