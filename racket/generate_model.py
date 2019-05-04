import numpy as np
import json

def getdata(idx, key='Right_Wrist', origo='Right_Shoulder'):
    data = json.load(open(f'data/data-{idx}.json', 'r'))
    data = sorted(data, key=lambda f: f['time'])
    y = [f[key]['y'] - f[origo]['y'] for f in data]
    x = [f[key]['x'] - f[origo]['x'] for f in data]
    t = [f['time'] - data[0]['time'] for f in data]
    return (x, y, t)

def make_interpolation_by_L2(x, y, t):
    n = len(x)
    assert n == len(y)
    L = [0]
    for i in range(n-1):
        L.append(np.sqrt((x[i+1]-x[i])**2 + (y[i+1] - y[i])**2) + L[-1])
    L = np.array(L)

    def interpolation(p):
        assert 0 <= p <= 1
        idx = np.where(L < p*L[-1])[0][-1]
        coeff = p - L[idx]/L[-1]
        return np.array(
            [(x[idx+1] - x[idx])*coeff + x[idx], (y[idx+1] - y[idx])*coeff + y[idx]])
    return interpolation

def make_interpolation_by_T(x, y, t):
    n = len(x)
    assert n == len(y)

    def interpolation(p):
        assert 0 <= p <= 1
        idx = np.where(t < p*t[-1])[0][-1]
        coeff = p - t[idx]/L[-1]
        return np.array(
            [(x[idx+1] - x[idx])*coeff + x[idx], (y[idx+1] - y[idx])*coeff + y[idx]])
    return interpolation

def make_final_model():
    interps = []
    for i in range(1, 18):
        x_, y_, t_ = getdata(i, key='Right_Wrist')
        #plt.plot(x_, y_, linestyle='dashed', linewidth=1)
        interps.append(make_interpolation_by_L2(x_, y_, t_))

    return lambda p: sum(interp(p) for interp in interps) / len(interps)
