import asyncio
import asyncio.events
import websockets

from threading import Lock
from datetime import datetime

import commands
import arm
import video

# Constants and configuration

ADDRESS = "0.0.0.0"
PORT = 8765
PING_DELAY = 5.0

# Code

class Main():
    current_client = None
    active = True

    is_sending = True
    is_receiving = True

    logging = ""
    logging_lock = Lock()

    data = ""

    server_task = None
    term_task = None
    arm_task = None
    video_task = None

    client_udp_port = None
    recv_queue = asyncio.Queue()

    def __str__(self):
        return f"\
Current client: {self.current_client}\n\
Client UDP port: {self.client_udp_port}\n\
Active: {self.active}\n\
sending: {self.is_sending}\n\
receiving: {self.is_receiving}\n\
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
            case _:
                print("Invalid attribute...\n")

    def log_print(self, toLog, shouldPrint = True):
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
        while self.active:
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
        while self.active:
            await asyncio.sleep(1)
            if self.is_receiving:
                received = await websocket.recv()
                await self.recv_queue.put(received)

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
            await asyncio.sleep(1)

    async def run_server(self):
        async with websockets.serve(self.handle_client, ADDRESS, PORT) as websocket:
            address = None
            port = None

            for socket in websocket.sockets:
                address = socket.getsockname()[0]
                port = socket.getsockname()[1]

            self.log_print(f"Server initiated at [{address}@{port}]\n", True)
            await websocket.serve_forever()

    async def run(self):
        try:
            self.server_task = asyncio.create_task(self.run_server())

            await asyncio.sleep(0.1)
            term_coroutine = asyncio.to_thread(self.run_terminal)
            self.term_task = asyncio.create_task(term_coroutine)
            
            await asyncio.sleep(0.1)
            arm_coroutine = asyncio.to_thread(arm.run_arm, self, asyncio.get_event_loop())
            self.arm_task = asyncio.create_task(arm_coroutine)

            await asyncio.sleep(0.1)
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
