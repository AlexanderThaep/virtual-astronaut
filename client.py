import asyncio
from websockets.asyncio.client import connect

import msgpack
import cv2 as cv
import numpy as np

class DatagramHandler(asyncio.DatagramProtocol):
    buffer = bytearray()
    img = None

    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        if (len(data) == 1):
            image_array = np.frombuffer(self.buffer.copy(), dtype=np.uint8)
            self.img = cv.imdecode(image_array, cv.IMREAD_COLOR)

            self.buffer.clear()
        else:
            self.buffer.extend(data)
            self.img = None

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
        _, protocol = await loop.create_datagram_endpoint(
            DatagramHandler,
            local_addr=("localhost", 3000))

        while True:
            await asyncio.sleep(0)
            if (protocol.img is not None):
                cv.imshow("Received feed", protocol.img)
                cv.waitKey(1)

if __name__ == "__main__":
    asyncio.run(receive())