import numpy as np
import json


def getdata(
    idx, key='Right_Wrist', origo='Right_Shoulder', scale='Right_Elbow'
):
    data = json.load(open(f'data/data-{idx}.json', 'r'))
    data = sorted(data, key=lambda f: f['time'])
    scale = np.array([np.linalg.norm(f[scale] - f[origo]) for f in data])
    y = np.array([(f[key]['y'] - f[origo]['y']) / scale for f in data]) / scale
    x = np.array([(f[key]['x'] - f[origo]['x']) / scale for f in data]) / scale
    t = [f['time'] - data[0]['time'] for f in data]
    return (x, y, t)


def make_interpolation_by_L2(x, y, t):
    n = len(x)
    assert n == len(y)
    L = [0]
    for i in range(n - 1):
        L.append(
            np.sqrt((x[i + 1] - x[i]) ** 2 + (y[i + 1] - y[i]) ** 2) + L[-1]
        )
    L = np.array(L)

    def interpolation(p):
        assert 0 <= p <= 1
        idx = np.where(L < p * L[-1])[0][-1]
        coeff = p - L[idx] / L[-1]
        return np.array(
            [
                (x[idx + 1] - x[idx]) * coeff + x[idx],
                (y[idx + 1] - y[idx]) * coeff + y[idx],
            ]
        )

    return interpolation


def make_interpolation_by_T(x, y, t):
    n = len(x)
    assert n == len(y)

    def interpolation(p):
        assert 0 <= p <= 1
        idx = np.where(t < p * t[-1])[0][-1]
        coeff = p - t[idx] / L[-1]
        return np.array(
            [
                (x[idx + 1] - x[idx]) * coeff + x[idx],
                (y[idx + 1] - y[idx]) * coeff + y[idx],
            ]
        )

    return interpolation


def make_final_models(keys, origo='Right_Shoulder', scale='Right_Elbow'):
    models = {}
    for key in keys:
        interps = []
        for i in range(1, 18):
            x_, y_, t_ = getdata(i, key=key, origo=origo, scale=scale)
            interps.append(make_interpolation_by_L2(x_, y_, t_))

        models[key] = lambda p: sum(interp(p) for interp in interps) / len(
            interps
        )
    return models


class FrameFollower:
    def __init__(self, keys, curves, radius=0.01, step=0.01):
        self._followers = {
            key: Follower(curves[key], radius=radius, step=step) for key in keys
        }
        self._keys = keys
        self._current_state_idx = 0

    def test(self, points):
        results = {
            key: follower.test(points[key], self._current_state_idx)
            for key, follower in self._followers.items()
        }
        if all(ok for ok, _ in results.values()):
            self._current_state_idx += 1
        return results


class Follower:
    def __init__(self, curve, radius=0.01, step=0.01):
        _params = np.arange(0, 1, step) + step
        self._states = [curve(p) for p in _params]

        self._radius = radius

        self._previous = np.array([0, 0])

    def test(self, point, state_idx):
        try:
            state = self._states[state_idx]
            ok = (
                np.linalg.norm(self._previous - point) > 0
                and np.cross(state - point, state - self._previous)
                / np.linalg.norm(self._previous - point)
                < self._radius
            )
            self._previous = point
            return (ok, state - self._previous)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(state_idx)
            print(len(self._states))
