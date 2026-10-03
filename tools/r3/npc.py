"""Supporting characters, built from the detective's rig and baked into a room set as part of the background.

Tiny and Vance sit still and talk from where they are (main.voice() in the game), so they don't need sprite
sheets of their own. place() poses the rig, recolours it, scales it and drops it into the room's Scene."""
import numpy as np
import detective
from scene3d import Ry

SEATED = dict(lhp=86, rhp=84, lk=88, rk=86, lfp=4, rfp=2, labd=7, rabd=7, lean=4, coatlen=0.14)


def _scale(S, s):
    for p in S.prims:
        for key in ('a', 'b', 'c', 'r'):
            p[key] = p[key] * s
        for key in ('ra', 'rb', 'k', 'shell'):
            p[key] = p[key] * s
        for key in ('clip', 'clip2'):
            if p[key] is not None:
                p[key] = (p[key][0], p[key][1] * s)
    S.decals = [(f, t, [(n, o * s) for n, o in pl], fe * s) for f, t, pl, fe in S.decals]


def _translate(S, t):
    t = np.asarray(t, float)
    for p in S.prims:
        if p['type'] in (0, 3):           # cones and spheres keep their positions in a / b
            p['a'] = p['a'] + t
            p['b'] = p['b'] + t
        p['c'] = p['c'] + t
        for key in ('clip', 'clip2'):
            if p[key] is not None:
                p[key] = (p[key][0], p[key][1] + float(np.asarray(p[key][0]) @ t))
    S.decals = [(f, to, [(n, o + float(np.asarray(n) @ t)) for n, o in pl], fe) for f, to, pl, fe in S.decals]


def place(S, name, pose, pos, yaw=0.0, scale=1.0, colors=None, tag=None):
    """Build the rig in `pose`, recolour materials (name -> rgb), turn it to `yaw` (0 = facing the camera's +z),
    scale it and add it to scene S standing (or sitting) at floor point `pos`."""
    R = detective.build(pose)
    for m, rgb in (colors or {}).items():
        vals = R.mats[R.mat_index[m]]
        R.mat(m, rgb, spec=vals[3], shin=vals[4], namp=vals[5], nscale=vals[6], bump=vals[7], bscale=vals[8],
              wrap=vals[9], aniso=vals[10])
    R.transform(Ry(yaw))
    _scale(R, scale)
    _translate(R, pos)
    remap = {}
    for mname, idx in R.mat_index.items():
        new = f'{name}_{mname}'
        S.mat_index[new] = len(S.mats)
        S.mats.append(list(R.mats[idx]))
        remap[idx] = S.mat_index[new]
    for p in R.prims:
        p = dict(p)
        p['mat'] = remap[p['mat']]
        if p.get('inmat') is not None:
            p['inmat'] = remap[p['inmat']]
        S.prims.append(p)
        if tag:
            S.tags.setdefault(tag, []).append(len(S.prims) - 1)
    for f, t, pl, fe in R.decals:
        S.decals.append((remap[f], remap[t], pl, fe))
