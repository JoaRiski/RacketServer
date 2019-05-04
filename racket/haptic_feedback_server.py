import random
import asyncio


class HapticFeedbackServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.messages = asyncio.Queue()

    async def handle(self, reader, writer):
        addr = writer.get_extra_info("peername")
        print(f"Received a new connection from {addr}")
        self.messages = asyncio.Queue()

        while True:
            message = await self.messages.get()

            # print(message)

            data = bytes([
                0,
                0,
                0,
                0,
                0,
                255 if message["Right_Elbow"][0] is False else 0,
                255 if message["Right_Wrist"][0] is False else 0,
                0,
            ])
            writer.write(data)
            print(f"Sending {data}")

            await writer.drain()

        print("Closes a client socket")
        writer.close()

    def get_task(self, event_loop):
        return asyncio.start_server(
            self.handle, self.host, self.port, loop=event_loop
        )
