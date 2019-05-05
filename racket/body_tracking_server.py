import asyncio
import json
from . import generate_model as models
import numpy as np
import pygame

ORIGO = 'Right_Shoulder'
SCALE = 'Body_Center'
KEYS = ['Right_Elbow', 'Right_Wrist']
COLORS = {'Right_Elbow': (255, 0, 0), 'Right_Wrist': (0, 255, 0)}

RADIUS = 0.2

pygame.init()
screen = pygame.display.set_mode((800, 800))
screen.fill((255, 255, 255))
s = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
follower_s = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)


screen.blit(s, (0, 0))
pygame.display.flip()


def to_pos(json):
    return np.array([json['x'], json['y']])


class BodyTrackingProtocol:
    def __init__(self, feedback_server):
        self._feedback_server = feedback_server

        self._models = models.make_final_models(KEYS, origo=ORIGO, scale=SCALE)
        self._follower = models.FrameFollower(KEYS, self._models, radius=RADIUS)

        for key, f in self._follower._followers.items():
            for idx, state in enumerate(f._states):
                pygame.draw.circle(
                    follower_s,
                    COLORS[key],
                    (int(400 + state[0] * 400), int(400 - state[1] * 400)),
                    5,
                    2 if idx == self._follower._current_state_idx else 0
                )

        print(self._models[KEYS[0]](0.9))
        print(self._models[KEYS[1]](0.9))
        # print(len(self._follower._followers))
        # print(self._follower._followers)

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.ensure_future(
            self._datagram_received(data, addr), loop=asyncio.get_running_loop()
        )

    async def _datagram_received(self, data, addr):
        message = data.decode()
        try:
            frame = json.loads(message)
        except Exception:
            return

        for key in KEYS:
            if key not in frame:
                return

        points = {}
        screen.fill((255, 255, 255))
        screen.blit(follower_s, (0, 0))

        scale = np.linalg.norm(to_pos(frame[SCALE]) - to_pos(frame[ORIGO]))

        for key in KEYS:
            unscaled_pos = (to_pos(frame[key]) - to_pos(frame[ORIGO]))
            pos = (to_pos(frame[key]) - to_pos(frame[ORIGO])) / scale
            points[key] = pos
            pygame.draw.circle(
                screen,
                COLORS[key],
                (int(400 + unscaled_pos[0] * 400), int(400 - unscaled_pos[1] * 400)),
                int(RADIUS * 400),
                2,
            )


        step_count = 1 / self._follower.step
        _current_state_idx = self._follower._current_state_idx + 1
        if _current_state_idx >= step_count:
            _current_state_idx = 0
        for follower in self._follower._followers.values():
            state = follower._states[_current_state_idx]
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (int(400 + state[0] * 400), int(400 - state[1] * 400)),
                int(5),
                2,
            )

        screen.blit(s, (0, 0))
        pygame.display.flip()

        data = self._follower.test(points)
        await self._feedback_server.messages.put(data)

    @staticmethod
    async def main(loop, feedback_server):
        import os

        transport, _ = await loop.create_datagram_endpoint(
            lambda: BodyTrackingProtocol(feedback_server),
            local_addr=(os.environ["UDP_IP"], 8888),
        )
