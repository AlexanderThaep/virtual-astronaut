import asyncio
import asyncio.events
import websockets.exceptions
import websockets.asyncio.server

from threading import Lock
from datetime import datetime

import commands
import arm
import video

# Constants and configuration

ADDRESS = "localhost"
PORT = 8765
PING_DELAY = 5.0

# Code

class Main():
    current_client = None
    active = True

    is_sending = False
    is_receiving = False

    logging = ""
    logging_lock = Lock()

    data = ""

    server_task = None
    term_task = None
    arm_task = None
    video_task = None

    recv_queue = asyncio.Queue()

    def __str__(self):
        return f"\
Current client: {self.current_client}\n\
Active: {self.active}\n\
Is sending: {self.is_sending}\n\
Is receiving: {self.is_receiving}\n\
Server Task: {self.server_task is not None}\n\
Terminal Task: {self.term_task is not None}\n\
Arm Task: {self.arm_task is not None}\n\
Video Task: {self.video_task is not None}\n\
Command queue: {self.recv_queue}\n"

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

    def task_finished_callback(self, task):
        try:
            task.exception()
        except asyncio.exceptions.CancelledError:
            return

    async def periodic_ping(self, seconds, websocket):
        while True:
            try:
                await asyncio.sleep(seconds)
                await websocket.ping()
            except websockets.exceptions.ConnectionClosed:
                self.current_client = None
                self.log_print(f"Client disconnected: {websocket.remote_address}\n", False)
                return
            except websockets.exceptions.ConcurrencyError:
                self.log_print("Concurrency error!\n", False)

            timestamp = datetime.now()
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            self.log_print(f"[{formatted_timestamp}] Heartbeat ping!\n", False)

    async def receive_commands(self, websocket):
        while True:
            await asyncio.sleep(0)
            result = await websocket.recv()
            await self.recv_queue.put(result)

    async def handle_client(self, websocket):
        if self.current_client is not None:
            self.log_print("Another client is already connected, lil' bro.\n", False)
            await websocket.close()
            return

        if self.current_client is None:
            self.current_client = websocket
            self.log_print(f"Client connected: {websocket.remote_address}\n", False)

        asyncio.create_task(self.periodic_ping(PING_DELAY, websocket)).add_done_callback(self.task_finished_callback)
        asyncio.create_task(self.receive_commands(websocket)).add_done_callback(self.task_finished_callback)

        while self.active:
            await asyncio.sleep(0)

    async def run_server(self):
        self.log_print(f"Server initiated at [{ADDRESS}@{PORT}]\n", True)
        async with websockets.serve(self.handle_client, ADDRESS, PORT) as websocket:
            await websocket.serve_forever()

    async def run(self):
        try:
            self.server_task = asyncio.create_task(self.run_server())

            term_coroutine = asyncio.to_thread(self.run_terminal)
            self.term_task = asyncio.create_task(term_coroutine)
            
            arm_coroutine = asyncio.to_thread(arm.run_arm, self)
            self.arm_task = asyncio.create_task(arm_coroutine)

            video_coroutine = asyncio.to_thread(video.run_video, self)
            self.video_task = asyncio.create_task(video_coroutine)

            await self.server_task
            await self.term_task
            await self.arm_task
            await self.video_task
        except asyncio.CancelledError:
            print("Terminated server.")

if __name__ == "__main__": 
    asyncio.run(Main().run())