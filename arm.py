import asyncio
import msgpack

async def loop(main, event_loop):
    while main.active:
        await asyncio.sleep(1)
        received = asyncio.run_coroutine_threadsafe(main.recv_queue.get(), event_loop).result()
        result = msgpack.unpackb(received, object_pairs_hook=dict)

        if result.get("Port"):
            main.client_udp_port = result["Port"]

        main.log_print(f"Command received: {result}\n", False)
    
def run_arm(main, event_loop):
    asyncio.run(loop(main, event_loop))