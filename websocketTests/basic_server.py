#!/usr/bin/env python

# WS server example

import asyncio
import websockets

async def hello(websocket, path):
    name = await websocket.recv()
    #print(f"< {name}")
    print("< {}".format(name))

    #greeting = f"Hello {name}!"
    greeting = "Hello {}!".format(name)

    await websocket.send(greeting)
    #print(f"> {greeting}")
    print("> {}".format(greeting))

start_server = websockets.serve(hello, '', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()