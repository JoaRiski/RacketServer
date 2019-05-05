import asyncio
import json
from . import generate_model as models
import numpy as np
import pygame

ORIGO = 'Right_Shoulder'
SCALE = 'Body_Center'
KEYS = ['Right_Elbow', 'Right_Wrist']
COLORS = {'Right_Elbow': (255, 150, 150), 'Right_Wrist': (0, 255, 0)}

SCREEN_SIZE = 800
CTR = int(SCREEN_SIZE / 2)

RADIUS = 0.15
ES_RADIUS = 0.18

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
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
        self._follower = models.FrameFollower(
            keys=KEYS,
            curves=self._models,
            radius=RADIUS,
            es_radius=ES_RADIUS
        )

        for key, f in self._follower._followers.items():
            for idx, state in enumerate(f._states):
                pygame.draw.circle(
                    follower_s,
                    COLORS[key],
                    (int(CTR + state[0] * CTR), int(CTR - state[1] * CTR)),
                    5,
                    2 if idx == self._follower._current_state_idx else 0
                )

        # print(self._models[KEYS[0]](0.9))
        # print(self._models[KEYS[1]](0.9))

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
            pos = (to_pos(frame[key]) - to_pos(frame[ORIGO])) / scale
            points[key] = pos
            pygame.draw.circle(
                screen,
                COLORS[key],
                (int(CTR + pos[0] * CTR), int(CTR - pos[1] * CTR)),
                int(RADIUS * CTR),
                2,
            )
            pygame.draw.circle(
                screen,
                COLORS[key],
                (int(CTR + pos[0] * CTR), int(CTR - pos[1] * CTR)),
                int(ES_RADIUS * CTR),
                2,
            )

        data = self._follower.test(points)
        for key in KEYS:
            if not data[key][0]:
                pos = points[key]
                pygame.draw.circle(
                    screen,
                    COLORS[key],
                    (int(CTR + pos[0] * CTR), int(CTR - pos[1] * CTR)),
                    int(RADIUS * CTR),
                )



        step_count = 1 / self._follower.step
        _current_state_idx = self._follower._current_state_idx
        if _current_state_idx >= step_count:
            _current_state_idx = 0
        for follower in self._follower._followers.values():
            state = follower._states[_current_state_idx]
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (int(CTR + state[0] * CTR), int(CTR - state[1] * CTR)),
                int(8),
                6,
            )

        screen.blit(s, (0, 0))
        pygame.display.flip()

        await self._feedback_server.messages.put(data)

    @staticmethod
    async def main(loop, feedback_server):
        import os

        transport, _ = await loop.create_datagram_endpoint(
            lambda: BodyTrackingProtocol(feedback_server),
            local_addr=(os.environ["UDP_IP"], 8888),
        )
