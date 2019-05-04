import sys
import asyncio
import pygame

from .body_tracking_server import BodyTrackingProtocol
from .haptic_feedback_server import HapticFeedbackServer


# We need to do this or Ctrl-C signal isn't processed
async def default_loop(loop):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop.stop()
        await asyncio.sleep(0.5)


class RacketServer:
    def __init__(self):
        self.event_loop = asyncio.get_event_loop()
        self.haptic_feedback_server = HapticFeedbackServer("0.0.0.0", 8889)

    def launch(self):
        self.event_loop.run_until_complete(
            self.haptic_feedback_server.get_task(self.event_loop)
        )
        self.event_loop.run_until_complete(
            BodyTrackingProtocol.main(
                self.event_loop, self.haptic_feedback_server
            )
        )
        self.event_loop.create_task(default_loop(self.event_loop))
        print("Running on 0.0.0.0 on ports 8888 and 8889")
        try:
            self.event_loop.run_forever()
        except KeyboardInterrupt:
            print("Stopping...")
            self.event_loop.stop()
