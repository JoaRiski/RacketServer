import asyncio
import json
from . import generate_model as models
import numpy as np

ORIGO = 'Right_Shoulder'
KEYS = ['Right_Elbow', 'Right_Wrist']


def to_pos(json):
    return np.array([json['x'], json['y']])


class BodyTrackingProtocol:
    def __init__(self, feedback_server):
        self._feedback_server = feedback_server

        self._models = models.make_final_models(KEYS, origo=ORIGO)
        self._follower = models.FrameFollower(KEYS, self._models)

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.ensure_future(
            self._datagram_received(data, addr), loop=asyncio.get_running_loop()
        )

    async def _datagram_received(self, data, addr):
        message = data.decode()
        frame = json.loads(message)

        points = {}
        for key in KEYS:
            pos = to_pos(frame[key]) - to_pos(frame[ORIGO])
            points[key] = pos

        data = self._follower.test(points)
        await self._feedback_server.messages.put(data)

    @staticmethod
    async def main(loop, feedback_server):
        transport, _ = await loop.create_datagram_endpoint(
            lambda: BodyTrackingProtocol(feedback_server),
            local_addr=("10.100.41.154", 8888),
        )

        try:
            print('Record server running at port 8888')
            await asyncio.sleep(3600)
        finally:
            transport.close()
