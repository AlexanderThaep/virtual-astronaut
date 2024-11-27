import asyncio
import asyncio.events
from websockets.asyncio.server import serve

from threading import Lock

# Constants and configuration

ADDRESS = "localhost"
PORT = 8765

# Other

data = ""
logging = ""

logging_lock = Lock()

# Code

def log_print(toLog, shouldPrint = True):
    global logging
    with logging_lock: logging += toLog
    if shouldPrint: print(toLog)

def get_input():
    while True:
        global data
        old = data
        data = input("Update data with: ")

        log_print(f"Old data: [{old}] ====> New data: [{data}]\n", True)

        global logging
        print(logging)

async def ping(websocket):
    global data
    await websocket.send(data)

    log_print(f"Sent data [{data}]\n", False)

async def run_server():
    log_print(f"Server initiated at [{ADDRESS}@{PORT}]\n", True)

    async with serve(ping, ADDRESS, PORT):
        await asyncio.get_running_loop().create_future()

async def main():
    server_task = asyncio.create_task(run_server()) 
    input_coroutine = asyncio.to_thread(get_input)
    input_task = asyncio.create_task(input_coroutine)

    await server_task
    await input_task

if __name__ == "__main__": 
    asyncio.run(main())