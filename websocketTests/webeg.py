#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets

counter=0

proxysock = object

async def controller_sim():
    while True:
        await asyncio.sleep(random.randint(0, 20) )
        global counter
        counter += 1
        #await websocket.send(now)
        await proxysock.send(str(counter))
        print("< counter = {}".format(counter))
        print('Controller at end of process')

async def time(websocket, path):
    global proxysock
    proxysock = websocket
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        await websocket.send(now)
#        await websocket.send(str(counter))
        await asyncio.sleep(random.random() * 30)

async def producer():
    global counter
    return counter

async def producer_handler(websocket, path):
    while True:
        message = await producer()
        await websocket.send(message)


async def main():

    start_server = websockets.serve(time, '', 5678)

    #ref = start_server.

    tasks = [controller_sim(), start_server]
    await asyncio.gather(*tasks)


#asyncio.run(main())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


# asyncio.get_event_loop().run_until_complete(main())
# print('got here')

# asyncio.get_event_loop().run_forever()
# print('got here 2')
