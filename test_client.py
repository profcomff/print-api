import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://localhost:8000/qr", extra_headers={"Authorization": 'token ADAQ-123456789'}) as websocket:
        async for message in websocket:
            print(message)

asyncio.run(hello())
