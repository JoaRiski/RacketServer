import numpy as np
import json


def to_pos(json):
    return np.array([json['x'], json['y']])


def getdata(idx, key, origo, scale):
    data = json.load(open(f'data/data-{idx}.json', 'r'))
    data = sorted(data, key=lambda f: f['time'])
    scale_ = np.array(
        [np.linalg.norm(to_pos(f[scale]) - to_pos(f[origo])) for f in data]
    )
    y = np.array([(f[key]['y'] - f[origo]['y']) for f in data]) / scale_
    x = np.array([(f[key]['x'] - f[origo]['x']) for f in data]) / scale_
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


def make_final_models(keys, origo, scale):
    models = {}
    for key in keys:
        interps = []
        for i in range(0, 8):
            x_, y_, t_ = getdata(i, key=key, origo=origo, scale=scale)
            interps.append(make_interpolation_by_L2(x_, y_, t_))

        def get_get_point(interps):
            def get_point(p):
                return sum([interp(p) for interp in interps]) / len(
                    interps
                )
            return get_point

        models[key] = get_get_point(interps)
    return models


class FrameFollower:
    def __init__(self, keys, curves, radius, es_radius, step=0.01):
        self.step = step
        self._followers = {
            key: Follower(curves[key], radius=radius, es_radius=es_radius, step=step)
            for key in keys
        }
        self._current_state_idx = 0

    def test(self, points):
        do_while = True
        while do_while:
            results = {
                key: follower.test(points[key], self._current_state_idx)
                for key, follower in self._followers.items()
            }
            all_ok = all(ok for ok, _, _ in results.values())
            if all_ok:
                self._current_state_idx += 1
            step_count = 1 / self.step
            if self._current_state_idx >= step_count:
                self._current_state_idx = 0
            do_while = all_ok
        return results


class Follower:
    def __init__(self, curve, radius, es_radius, step=0.01):
        _params = np.arange(0, 1, step) + step
        self._states = [curve(p) for p in _params]

        self._radius = radius
        self._es_radius = es_radius

        self._previous = np.array([0, 0])

    def test(self, point, state_idx):
        try:
            state = self._states[state_idx]
            norm = np.linalg.norm(state - point)
            ok = norm < self._radius
            es = norm < self._es_radius
            return (ok, state - point, es)
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(state_idx)
            print(len(self._states))

    def __repr__(self):
        return str(vars(self))
