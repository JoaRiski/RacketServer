import asyncio
import json
import generate_model as models
import numpy as np

ORIGO = 'Right_Shoulder'
KEYS = ['Right_Elbow', 'Right_Wrist']


def to_pos(json):
    return np.array([json['x'], json['y']])


class BodyTrackingServer:
    def __init__(self, host, port, feedback_server):
        self.host = host
        self.port = port

        self._feedback_server = feedback_server

        self._models = models.make_final_models(KEYS, origo=ORIGO)
        self._follower = models.FrameFollower(KEYS, self._models)

    async def handle(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        frame = json.loads(message)

        points = {}
        for key in KEYS:
            pos = to_pos(frame[key]) - to_pos(frame[ORIGO])
            points[key] = pos

        data = self._follower.test(points)
        await self._feedback_server.messages.put(data)

        writer.close()

    def get_task(self, event_loop):
        return asyncio.start_server(
            self.handle, self.host, self.port, loop=event_loop
        )
