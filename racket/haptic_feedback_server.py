import random
import asyncio

def should_es(message, key, up):
    ok = message[key][1][1] > 0 if up else message[key][1][1] < 0
    return not message[key][2] and ok

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
                255 if should_es(message, 'Right_Elbow', up=False) else 0,
                255 if should_es(message, 'Right_Elbow', up=True) else 0,
                0,
                0,
                0,
                0,
                255 if should_es(message, 'Right_Wrist', up=False) else 0,
                255 if should_es(message, 'Right_Wrist', up=True) else 0,
            ])
            writer.write(data)

            await writer.drain()

        print("Closes a client socket")
        writer.close()

    def get_task(self, event_loop):
        return asyncio.start_server(
            self.handle, self.host, self.port, loop=event_loop
        )
