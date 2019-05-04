import asyncio
import json
import generate_model as models

ORIGO = 'Right_Shoulder'
KEYS = ['Right_Elbow', 'Right_Wrist']


class BodyTrackingServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self._models = models.make_final_models(KEYS, origo=ORIGO)
        self._followers = {
            key: models.Follower(model) for key, model in self._models.items()
        }

    async def handle(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        frame = json.loads(message)



        writer.close()

    def get_task(self, event_loop):
        return asyncio.start_server(
            self.handle, self.host, self.port, loop=event_loop
        )
