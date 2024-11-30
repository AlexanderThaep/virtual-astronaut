import asyncio
from websockets.asyncio.client import connect

import msgpack
import cv2 as cv
import numpy as np

# Copied from the docs
class DatagramHandler(asyncio.DatagramProtocol):
    buffer = bytearray()
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        self.buffer.extend(data)
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
        transport, protocol = await loop.create_datagram_endpoint(
            DatagramHandler,
            local_addr=("localhost", 3000))

        await asyncio.sleep(2)
        print(len(protocol.buffer))
        image_array = np.frombuffer(protocol.buffer, dtype=np.uint8)
        img = cv.imdecode(image_array, cv.IMREAD_COLOR)
        cv.imshow("Received image", img)
        cv.waitKey()

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(receive())