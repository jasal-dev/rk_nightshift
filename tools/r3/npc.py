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


# ---------------------------------------------------------------- Case 2 cast: looks (rig options + colours) and poses
STAND = dict(lsp=-2, le=14, rsp=-2, re=14)
ARMS_FOLDED = dict(lsp=34, lsa=12, le=118, lin=96, rsp=30, rsa=12, re=106, rin=100)   # forearms crossed over the chest
CROUCH = dict(lhp=96, lk=112, lfp=14, rhp=4, rk=100, rfp=-60, labd=8, rabd=6, lean=22, coatlen=0.2)

CAST = {
    # Dr. Anita Shah, coroner's investigator: navy windbreaker, hair pinned up
    'shah': (dict(stubble=False, hair='bun', coatlen=0.12),
             dict(coat=(38, 46, 72), coat_dk=(28, 32, 52), lining=(30, 34, 50), shirt=(150, 150, 156), pants=(40, 40, 46),
                  hair=(26, 22, 22), hairgrey=(52, 48, 46), brow=(30, 24, 22), skin=(150, 104, 80), skin_dk=(124, 84, 66),
                  lips=(132, 86, 74))),
    # Officer Lena Park: patrol cap, long black rain cape
    'park': (dict(stubble=False, hair='cap', coatlen=0.5),
             dict(coat=(26, 30, 40), coat_dk=(18, 20, 28), lining=(20, 22, 30), shirt=(40, 52, 80), pants=(30, 34, 48),
                  hair=(20, 18, 18), hairgrey=(20, 18, 18), brow=(26, 22, 20), skin=(196, 152, 122), skin_dk=(168, 126, 100),
                  lips=(170, 112, 100), cap=(26, 30, 46))),
    # Rosa: waitress in her sixties, salmon uniform dress, grey bun with a pencil in it
    'rosa': (dict(stubble=False, hair='bun_pencil', coatlen=0.44),
             dict(coat=(196, 112, 96), coat_dk=(160, 86, 74), lining=(230, 226, 214), shirt=(236, 232, 222),
                  pants=(150, 120, 104), hair=(176, 172, 168), hairgrey=(196, 194, 190), brow=(120, 112, 108),
                  skin=(176, 124, 98), skin_dk=(146, 100, 80), lips=(160, 84, 78))),
    # Hector "Heck" Dominguez: teal Glide jacket
    'heck': (dict(hair='full', coatlen=0.04),
             dict(coat=(30, 128, 116), coat_dk=(22, 92, 84), lining=(30, 40, 40), shirt=(36, 36, 40), pants=(52, 58, 76),
                  hair=(24, 20, 18), hairgrey=(44, 40, 38), brow=(24, 20, 18), stubble=(110, 80, 62), skin=(160, 110, 82),
                  skin_dk=(130, 88, 66))),
    # Devin Clark: grey hoodie, sweatpants, wet dark hair, a little beard
    'devin': (dict(hair='full', coatlen=0.02),
              dict(coat=(124, 126, 132), coat_dk=(100, 102, 108), lining=(70, 72, 78), shirt=(44, 46, 50), pants=(66, 68, 74),
                   hair=(30, 26, 24), hairgrey=(30, 26, 24), brow=(34, 28, 24), stubble=(120, 94, 80), skin=(198, 160, 136),
                   skin_dk=(170, 134, 112), shoe=(200, 200, 204))),
    # Kenji Ota: dark bomber jacket
    'kenji': (dict(stubble=False, hair='full', coatlen=0.02, blink=1.0),
              dict(coat=(40, 44, 50), coat_dk=(30, 32, 36), lining=(60, 30, 30), shirt=(170, 172, 176), pants=(46, 50, 62),
                   hair=(18, 16, 16), hairgrey=(18, 16, 16), brow=(20, 18, 18), skin=(184, 146, 118), skin_dk=(156, 120, 96))),
    # Norm's counter: two cabbies, a nurse off a double, a security guard asleep over his eggs
    'cabbie1': (dict(hair='short', coatlen=0.06),
                dict(coat=(92, 64, 44), coat_dk=(70, 48, 34), shirt=(150, 140, 120), pants=(50, 50, 56), skin=(150, 108, 84))),
    'cabbie2': (dict(hair='full', coatlen=0.04, stubble=False),
                dict(coat=(60, 70, 50), coat_dk=(46, 54, 38), shirt=(180, 170, 150), pants=(40, 40, 46),
                     hair=(60, 40, 30), hairgrey=(60, 40, 30), skin=(110, 76, 58), skin_dk=(90, 62, 48))),
    'nurse': (dict(hair='long', stubble=False, coatlen=0.02),
              dict(coat=(70, 120, 150), coat_dk=(56, 98, 124), lining=(70, 120, 150), shirt=(70, 120, 150),
                   pants=(70, 120, 150), hair=(90, 60, 40), hairgrey=(90, 60, 40), brow=(80, 56, 40), skin=(200, 160, 136),
                   skin_dk=(170, 132, 112))),
    'guard': (dict(hair='cap', coatlen=0.06),
              dict(coat=(40, 40, 46), coat_dk=(30, 30, 34), shirt=(150, 150, 160), pants=(36, 36, 40), cap=(36, 36, 40),
                   skin=(120, 84, 64), skin_dk=(100, 70, 54))),
}


def cast(S, who, pose, pos, yaw=0.0, scale=1.0, tag=None):
    """Place a member of the Case 2 cast: their look from CAST, merged with `pose`."""
    look, colors = CAST[who]
    place(S, who + (('_' + tag) if tag else ''), {**look, **pose}, pos, yaw=yaw, scale=scale, colors=colors, tag=tag)
