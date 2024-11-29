import asyncio
import websockets.exceptions
from websockets.asyncio.client import connect

async def receive():
    uri = "ws://localhost:8765"
    async with connect(uri) as websocket:
        await asyncio.sleep(1)
        await websocket.send("Beans!")
        try:
            async for message in websocket:
                print(message)

        except websockets.exceptions.ConnectionClosed:
            print("Connection closed!\n")

if __name__ == "__main__":
    asyncio.run(receive())