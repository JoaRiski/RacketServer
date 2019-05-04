import asyncio


class HapticFeedbackServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handle(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))

        print("Send: %r" % message)
        writer.write(data)
        await writer.drain()

        print("Close the client socket")
        writer.close()

    def get_task(self, event_loop):
        return asyncio.start_server(
            self.handle, self.host, self.port, loop=event_loop
        )
