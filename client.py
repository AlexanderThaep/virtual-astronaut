import asyncio
import websockets.exceptions
from websockets.asyncio.client import connect

import msgpack

# Copied from the docs
class DatagramHandler(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        print(f"Data received: {data} from {addr}")

# Original

host_addr = "localhost"
host_port = 8765

packer = msgpack.Packer() 

async def receive():
    uri = f"ws://{host_addr}:{host_port}"
    async with connect(uri) as websocket:
        await asyncio.sleep(1)

        packed = msgpack.packb({"Port": 3000}) 
        await websocket.send(packed)
        # try:
        #     async for message in websocket:
        #         print(message)

        # except websockets.exceptions.ConnectionClosed:
        #     print("Connection closed!\n")
        
        loop = asyncio.get_running_loop()
        await loop.create_datagram_endpoint(
            DatagramHandler,
            local_addr=("localhost", 3000))
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(receive())