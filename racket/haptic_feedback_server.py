import random
import queue
import asyncio


class HapticFeedbackServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.messages = queue.Queue()

    async def handle(self, reader, writer):
        addr = writer.get_extra_info("peername")
        print(f"Received a new connection from {addr}")

        for i in range(20):
            message = self.messages.get()

            # TODO map to motors

            writer.write(message)

            await writer.drain()
            await asyncio.sleep(1)

        print("Closes a client socket")
        writer.close()

    def get_task(self, event_loop):
        return asyncio.start_server(
            self.handle, self.host, self.port, loop=event_loop
        )
