import asyncio
from websockets.asyncio.client import connect

async def receive():
    uri = "ws://localhost:8765"
    async with connect(uri) as websocket:
        gospel = await websocket.recv()
        print(f"<<< {gospel}")

if __name__ == "__main__":
    asyncio.run(receive())