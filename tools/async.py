import asyncio

async def speak():
    print('C')
    await asyncio.sleep(1)
    return 'D'

async def run():
    will_speak = asyncio.ensure_future(speak())
    await asyncio.sleep(2)
    print('A')
    print('B')
    print(await will_speak)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())