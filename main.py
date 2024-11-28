import asyncio
import asyncio.events
import websockets.exceptions
from websockets.asyncio.server import serve

from threading import Lock
import cv2
from datetime import datetime

import commands

# Constants and configuration

ADDRESS = "localhost"
PORT = 8765
PING_DELAY = 5.0

img = cv2.imread("doge.png")
img_data = cv2.imencode('.png', img)[1].tobytes()

# Code

class Main():
    current_client = None
    active = True

    is_sending = False
    is_receiving = False

    data = "beans"
    logging = ""

    logging_lock = Lock()

    server_task = None
    input_task = None

    def toggle(self, words : str):
        truth = words[1].lower() in ['true', '1', 't', 
                             'y', 'yes', 'yeah', 
                             'yup', 'certainly', 
                             'uh-huh']
        
        match (words[0]):
            case "sending":
                self.is_sending = truth
                print(self.is_sending)
            case "receiving":
                self.is_receiving = truth
                print(self.is_receiving)
            case "_":
                print("Invalid attribute...\n")

    def log_print(self, toLog, shouldPrint = True):
        global logging
        with self.logging_lock: self.logging += toLog
        if shouldPrint: print(toLog)

    def run_terminal(self):
        commands.CommandShell(main=self).cmdloop()

    async def periodic_ping(self, seconds, websocket):
        while True:
            await asyncio.sleep(seconds)
            await websocket.ping()

            timestamp = datetime.now()
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            self.log_print(f"[{formatted_timestamp}] Heartbeat ping!\n", False)

    async def handle_client(self, websocket):
        if self.current_client is not None:
            self.log_print("Another client is already connected, lil' bro.\n", False)
            await websocket.close()
            return

        if self.current_client is None:
            self.current_client = websocket
            self.log_print(f"Client connected: {websocket.remote_address}\n", False)

        asyncio.create_task(self.periodic_ping(PING_DELAY, websocket))

        while self.active:
            await asyncio.sleep(0)
            try:
                if (self.is_sending):
                    await websocket.send(self.data)
                if (self.is_receiving):
                    received = await websocket.recv()
                    self.log_print(f"Received data [{received}]\n", False)
            except websockets.exceptions.ConnectionClosed:
                self.current_client = None
                self.log_print(f"Client disconnected: {websocket.remote_address}\n", False)
                break

    async def run_server(self):
        self.log_print(f"Server initiated at [{ADDRESS}@{PORT}]\n", True)
        async with websockets.serve(self.handle_client, ADDRESS, PORT) as websocket:
            await websocket.serve_forever()

    async def run(self):
        try:
            self.server_task = asyncio.create_task(self.run_server()) 
            input_coroutine = asyncio.to_thread(self.run_terminal)
            self.input_task = asyncio.create_task(input_coroutine)

            await self.server_task
            await self.input_task
        except asyncio.CancelledError:
            print("Terminated server.")

if __name__ == "__main__": 
    asyncio.run(Main().run())