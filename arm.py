import asyncio

async def loop(main, event_loop):
    while main.active:
        await asyncio.sleep(0)
        command = asyncio.run_coroutine_threadsafe(main.recv_queue.get(), event_loop).result()

        main.log_print(f"Command received: {command}\n", False)

def run_arm(main, event_loop):
    asyncio.run(loop(main, event_loop))