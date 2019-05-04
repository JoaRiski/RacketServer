import asyncio
import json

DATA_COUNT = 0
FRAMES = []


class RecordProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        global FRAMES, DATA_COUNT
        message = data.decode()
        print('Received %r from %s' % (message, addr))

        if message.lower().startswith('end'):
            with open(f'data/data-{DATA_COUNT}.json', 'w') as f:
                f.write(json.dumps(FRAMES))
            FRAMES = []
            DATA_COUNT += 1
            self.transport.sendto(b'ENDED', addr)
            return

        FRAMES.append(json.loads(message))

        self.transport.sendto(data, addr)

async def main():
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        RecordProtocol, local_addr=("10.100.41.154", 8888)
    )

    try:
        print('Record server running at port 8888')
        await asyncio.sleep(3600)
    finally:
        transport.close()

asyncio.run(main())
