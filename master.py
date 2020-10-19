#!/usr/bin/env python3

import asyncio

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

WORKER_LIST = [
    {
        "host": "127.0.0.1",
        "port": 65430,
        "conn": 0
    },
    {
        "host": "127.0.0.1",
        "port": 65425,
        "conn": 0
    },
    {
        "host": "127.0.0.1",
        "port": 65420,
        "conn": 0
    }
]

async def contact_worker(message, host, port):
    message = str(message)
    reader, writer = await asyncio.open_connection(host, port)

    writer.write(message.encode())
    await writer.drain() # Flow control

    data = ""
    while True:
        MAX_BYTES = 1024
        chunk = await reader.read(MAX_BYTES)
        data += chunk.decode()
        if len(chunk) < MAX_BYTES:
            break

    writer.close()
    await writer.wait_closed()

    return data

async def master_server(reader, writer):
    data = ""
    while True:
        MAX_BYTES = 1024
        chunk = await reader.read(MAX_BYTES)  # Max number of bytes to read
        data += chunk.decode()
        if len(chunk) < MAX_BYTES:
            break
    
    print(WORKER_LIST)

    chosen_worker = None
    while True:
        for worker in WORKER_LIST:
            if worker["conn"] == 0:
                worker["conn"] += 1
                chosen_worker = worker
                break
        if chosen_worker:
            break
        await asyncio.sleep(10) # check connection every 10 seconds
    
    processed_data = await contact_worker(data, chosen_worker["host"], chosen_worker["port"])
    chosen_worker["conn"] -= 1

    writer.write(processed_data.encode())
    await writer.drain()  # Flow control
    writer.close()
    await writer.wait_closed()

async def main(host, port):
    server = await asyncio.start_server(master_server, host, port)
    await server.serve_forever()

asyncio.run(main(HOST, PORT))