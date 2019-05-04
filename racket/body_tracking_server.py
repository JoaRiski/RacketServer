import asyncio
import json
import generate_model as models

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
        self._followers = {
            key: models.Follower(model) for key, model in self._models.items()
        }

    async def handle(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        frame = json.loads(message)

        data = {}

        for key in KEYS:
            follower = self._followers[key]
            direction = follower.test(to_pos(frame[key]))
            data[key] = direction

        await self._feedback_server.messages.put(data)

        writer.close()

    def get_task(self, event_loop):
        return asyncio.start_server(
            self.handle, self.host, self.port, loop=event_loop
        )
