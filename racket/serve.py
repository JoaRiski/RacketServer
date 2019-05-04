import sys
import asyncio

from .body_tracking_server import BodyTrackingServer
from .haptic_feedback_server import HapticFeedbackServer


# We need to do this or Ctrl-C signal isn't processed
async def default_loop():
    while True:
        await asyncio.sleep(0.5)


class RacketServer:

    def __init__(self):
        self.event_loop = asyncio.get_event_loop()
        self.haptic_feedback_server = HapticFeedbackServer("0.0.0.0", 8889)
        self.body_tracking_server = BodyTrackingServer("0.0.0.0", 8888)

    def launch(self):
        self.event_loop.run_until_complete(
            self.haptic_feedback_server.get_task(self.event_loop)
        )
        self.event_loop.run_until_complete(
            self.body_tracking_server.get_task(self.event_loop)
        )
        self.event_loop.create_task(default_loop())
        print("Running on 0.0.0.0 on ports 8888 and 8889")
        try:
            self.event_loop.run_forever()
        except KeyboardInterrupt:
            print("Stopping...")
            self.event_loop.stop()
