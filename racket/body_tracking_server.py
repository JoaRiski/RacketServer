import asyncio
import json
from . import generate_model as models
import numpy as np

ORIGO = 'Right_Shoulder'
SCALE = 'Right_Elbow'
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

        for key in KEYS:
            if key not in frame:
                return

        points = {}
        scale = np.linalg.norm(to_pos(frame[ORIGO]) - to_pos(frame[SCALE]))
        for key in KEYS:
            pos = (to_pos(frame[key]) - to_pos(frame[ORIGO])) / scale
            points[key] = pos

        data = self._follower.test(points)
        await self._feedback_server.messages.put(data)

    @staticmethod
    async def main(loop, feedback_server):
        import os
        transport, _ = await loop.create_datagram_endpoint(
            lambda: BodyTrackingProtocol(feedback_server),
            local_addr=(os.environ["UDP_IP"], 8888),
        )
