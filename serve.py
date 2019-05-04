import asyncio


class HapticFeedbackServer:

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

class BodyTrackingServer:

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


body_tracking_server = BodyTrackingServer()
haptic_feedback_server = HapticFeedbackServer()

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(asyncio.start_server(
        body_tracking_server.handle,
        "0.0.0.0",
        8888,
        loop=loop,
    ))
    loop.run_until_complete(asyncio.start_server(
        haptic_feedback_server.handle,
        "0.0.0.0",
        8889,
        loop=loop,
    ))
    print("Running on 0.0.0.0 on ports 8888 and 8889")
    loop.run_forever()
except KeyboardInterrupt:
    pass

# server.close()
# loop.run_until_complete(server.wait_closed())
# loop.close()
