"""The detective: a present-day, late-career homicide detective. 3D rig rendered as pixel-art sprites.
Dark sport coat, open-collar shirt, no tie, badge clipped to the belt, salt-and-pepper hair, stubble."""
import math
import numpy as np
from scene3d import Scene, Frame, A, nrm, Rx, Ry, Rz, swing, WORLD


def materials(S):
    # Procedural noise stays at or above ~3 sprite pixels (1 px is about 6 mm): anything finer re-samples
    # differently on every animation frame and makes the figure shimmer in the game.
    # matte, slightly noisy surfaces: reads like film rather than plastic
    S.mat('skin',     (168, 124, 102), spec=0.06, shin=12, namp=0.10, nscale=60,  bump=0.05, bscale=40, wrap=0.35)
    S.mat('skin_dk',  (138, 98, 82),   spec=0.04, shin=12, namp=0.10, nscale=60,  bump=0.05, bscale=40, wrap=0.35)
    S.mat('hair',     (82, 76, 72),    spec=0.10, shin=18, namp=0.35, nscale=60, bump=0.25, bscale=40, aniso=1)
    S.mat('hairgrey', (140, 136, 132), spec=0.10, shin=18, namp=0.35, nscale=60, bump=0.25, bscale=40, aniso=1)
    S.mat('coat',     (84, 76, 66),    spec=0.02, shin=6,  namp=0.10, nscale=60, bump=0.03, bscale=40)
    S.mat('coat_dk',  (58, 52, 46),    spec=0.02, shin=6,  namp=0.10, nscale=60, bump=0.03, bscale=40)
    S.mat('vest',     (120, 132, 146), spec=0.02, shin=8,  namp=0.06, nscale=60, bump=0.06, bscale=40)
    S.mat('shirt',    (128, 136, 148), spec=0.02, shin=8,  namp=0.06, nscale=60, bump=0.06, bscale=40)
    S.mat('tie',      (186, 204, 222), spec=0.02, shin=8)
    S.mat('jacket',   (44, 45, 50),    spec=0.02, shin=8,  namp=0.12, nscale=60, bump=0.08, bscale=40)
    S.mat('pants',    (46, 46, 50),    spec=0.02, shin=8,  namp=0.08, nscale=60, bump=0.03, bscale=40)
    S.mat('shoe',     (30, 26, 24),    spec=0.25, shin=30, namp=0.10, nscale=60)
    S.mat('sole',     (18, 16, 15),    spec=0.02)
    S.mat('eyew',     (92, 82, 74),  spec=0.4, shin=60, wrap=0.3)
    S.mat('iris',     (52, 42, 34),    spec=0.6, shin=90)
    S.mat('pupil',    (14, 12, 12),    spec=0.6, shin=90)
    S.mat('lips',     (152, 106, 92),  spec=0.06, shin=20, wrap=0.35)
    S.mat('mouthin',  (50, 22, 22))
    S.mat('stubble',  (150, 114, 98),   spec=0.02, shin=10, namp=0.35, nscale=60, wrap=0.3)
    S.mat('brow',     (64, 56, 52),    spec=0.02, namp=0.3, nscale=60, aniso=1)
    S.mat('gold',     (200, 160, 70),  spec=1.0, shin=60, namp=0.06, nscale=60)
    S.mat('leather',  (34, 26, 22),    spec=0.15, shin=24, namp=0.08, nscale=60)
    S.mat('paper',    (226, 220, 200), spec=0.02, namp=0.02, nscale=60)
    S.mat('card',     (166, 128, 86),  spec=0.03, namp=0.05, nscale=60)
    S.mat('pen',      (22, 22, 26),    spec=0.6, shin=60)
    S.mat('steel',    (150, 150, 156), spec=0.8, shin=50)
    S.mat('button',   (28, 24, 22),    spec=0.3, shin=30)
    S.mat('lining',   (52, 40, 38),    spec=0.04, shin=16, namp=0.08, nscale=60)
    S.mat('belt',     (24, 20, 18),    spec=0.2, shin=24, namp=0.05, nscale=60)
    S.mat('buckle',   (150, 150, 154), spec=0.8, shin=50)
    S.mat('phone',    (20, 22, 26),    spec=0.6, shin=60)
    S.mat('screen',   (40, 60, 90), emis=(120, 170, 230), emis_mult=1.5)
    # only used by the supporting cast (npc.py), recoloured per character
    S.mat('cap',      (30, 34, 50),    spec=0.3, shin=30, namp=0.05, nscale=60)
    S.mat('torch',    (40, 40, 44),    spec=0.8, shin=50)
    S.mat('torch_lit', (255, 240, 210), emis=(255, 240, 210), emis_mult=6)
    S.mat('sock',     (60, 56, 58),    spec=0.02, shin=8,  namp=0.08, nscale=60)
    S.mat('pipe',     (70, 40, 24),    spec=0.5, shin=40)
    S.mat('umbrella', (22, 22, 26),    spec=0.4, shin=30, namp=0.05, nscale=60)
    S.mat('glass_c',  (150, 160, 166), spec=1.6, shin=90, refl=0.3)
    S.mat('water_c',  (120, 140, 150), spec=1.2, shin=90)


COAT_LEN = 0.40  # how far the overcoat hangs below the hip joint (m): just above the knee

# ---------------------------------------------------------------- the detective
DEFAULT = dict(yaw=90, lean=0, cyaw=0, pyaw=0, sway=0, dx=0, breath=0, shrug=0,
               lhp=5, labd=2.5, lk=3, lfp=0, rhp=-4, rabd=2.5, rk=3, rfp=0,
               lsp=-2, lsa=9, le=12, lin=4, lw=0, lroll=0, lhand='relaxed',
               rsp=-2, rsa=9, re=12, rin=4, rw=0, rroll=0, rhand='relaxed',
               hp=0, hy=0, hr=0, mouth=0, blink=0, props=(), coatlen=COAT_LEN, coatswing=0,
               stubble=True, hair='short', mustache=False, earring=None, noshoe=None, shoelen=1.0, cop=True,
               beard=False, headset=False, sleeves='coat')
# supporting cast only: stubble=False, hair = 'short' (receding) | 'full' | 'bun' | 'bun_pencil' | 'long' | 'cap'
#   | 'long_side' (down over the left ear and cheek) | 'bald' (a fringe at the back) | 'derby' (bowler hat),
# hr = head roll (degrees, + tilts toward the figure's left), mustache (a short toothbrush one),
# earring = 'l' / 'r' (one gold stud), noshoe = 'l' / 'r' (that foot in its sock), shoelen (shoe length scale),
# cop = False drops the badge and holster from the belt, beard (a full one, in the hair colour), headset (a band over
# the head and a mic at the mouth), sleeves = 'shirt' (shirtsleeves under a sleeveless vest or robe-less coat),
# hair = 'hood' (a hoodie's hood up, in the coat colour)

def leg_geo(pel, side, hp, abd, knee, fp):
    hip = pel.to((side * 0.092, -0.035, 0.0))
    base = pel.M @ Rz(side * abd)
    th = pel.M @ swing(hp) @ Rz(side * abd) @ A(0, -1, 0)
    knee_p = hip + 0.44 * th
    sh = pel.M @ swing(hp - knee) @ Rz(side * abd) @ A(0, -1, 0)
    ank = knee_p + 0.43 * sh
    a = math.radians(fp)
    fwd = pel.M @ A(0, math.sin(a), math.cos(a)); up = pel.M @ A(0, math.cos(a), -math.sin(a))
    foot = Frame(ank, np.column_stack([pel.M @ A(1, 0, 0), up, fwd]))
    return hip, knee_p, ank, foot

def build(p):
    p = {**DEFAULT, **p}
    S = Scene()
    materials(S)
    # --- legs relative to pelvis, ground solve
    pel0 = Frame((0, 0, 0), Ry(p['pyaw']) @ Rz(p['sway']))
    lows = []
    for side, k in ((1, 'l'), (-1, 'r')):
        hip, kn, ank, foot = leg_geo(pel0, side, p[k + 'hp'], p[k + 'abd'], p[k + 'k'], p[k + 'fp'])
        for zz in (-0.075, 0.0, 0.1, 0.19):
            lows.append(foot.to((0, -0.078, zz))[1])
        lows.append(kn[1] - 0.06)
    hy = -min(lows)
    pel = Frame((p['dx'], hy, 0), pel0.M)
    chest = Frame(pel.o, pel.M @ Ry(p['cyaw']) @ Rx(p['lean']))
    br, sg = p['breath'], p['shrug']

    # --- legs
    for side, k in ((1, 'l'), (-1, 'r')):
        hip, kn, ank, foot = leg_geo(pel, side, p[k + 'hp'], p[k + 'abd'], p[k + 'k'], p[k + 'fp'])
        S.cone(hip, kn, 0.08, 0.06, 'pants', k=0.03)
        S.cone(kn, ank + (ank - kn) * 0.02, 0.058, 0.049, 'pants', k=0.012)
        S.ell(foot, (0, 0.035, -0.005), (0.053, 0.048, 0.05), 'pants', k=0.015)       # trouser break
        sh, so, sl = ('sock', 'sock', 0.85) if p['noshoe'] == k else ('shoe', 'sole', p['shoelen'])
        S.ell(foot, (0, -0.03, 0.06 * sl), (0.048, 0.044, 0.138 * sl), sh, k=0.025,
              clip=(foot.M @ A(0, 1, 0), float(foot.M @ A(0, 1, 0) @ foot.to((0, -0.068, 0)))))
        S.ell(foot, (0, -0.035, -0.04), (0.042, 0.042, 0.05), sh, k=0.05)
        S.ell(foot, (0, -0.07, 0.055 * sl), (0.046, 0.007, 0.138 * sl), so)
        S.ell(foot, (0, -0.066, -0.045), (0.038, 0.012, 0.042), so)

    # --- trousers seat + belt
    S.ell(pel, (0, -0.02, -0.004), (0.146, 0.105, 0.1), 'pants', k=0.04)
    S.decal(pel, 'pants', 'belt', [((0, 1, 0), 0.077), ((0, -1, 0), -0.04)])
    S.box(pel, (0, 0.058, 0.103), (0.018, 0.015, 0.004), 0.002, 'buckle')
    if p['cop']:
        S.box(pel, (0.058, 0.045, 0.1), (0.02, 0.026, 0.005), 0.003, 'gold', rot=Ry(12))      # badge on the belt
        S.box(pel, (-0.15, 0.0, 0.02), (0.022, 0.07, 0.045), 0.012, 'leather')               # holster

    # --- shirt (inner torso), seen through the open coat
    S.ell(chest, (0, 0.37 + br, 0.0), (0.152, 0.14, 0.112 + br * 0.4), 'shirt', k=0.05)
    S.box(chest, (0, 0.25, 0.0), (0.142, 0.24, 0.104), 0.06, 'shirt', k=0.05)
    for yy in (0.13, 0.22, 0.31):
        S.sph(chest.to((0, yy, 0.112)), 0.0055, 'button')
    S.cone(chest.to((0, 0.55 + br, -0.002)), chest.to((0, 0.615 + br, 0.006)), 0.062, 0.055, 'shirt')
    S.decal(chest, 'shirt', 'skin', [((1, 0.35, 0), 0.016 + 0.35 * 0.6), ((-1, 0.35, 0), 0.016 + 0.35 * 0.6),
                                     ((0, 0, -1), -0.03), ((0, -1, 0), -0.5)])            # open collar

    # --- overcoat torso: two shell halves, open down the front in a long V
    al, oo = 0.125, -0.066        # opening edge: x = 0.06 at the waist, 0.11 at the chest (front surface)
    for s in (1, -1):
        S.tcyl(chest, (0, 0.245 + br * 0.5, 0.0), (0.178, 0.132 + br * 0.4), (0.166, 0.124), 0.245, 'coat',
               shell=0.011, clip=((s, -al, -1), oo), clip2=((s, 0, 0), 0.0), inmat='lining', k=0.0)
        # wide lapels folded back along the opening
        S.box(chest, (s * 0.122, 0.39 + br, 0.116), (0.038, 0.105, 0.0035), 0.003, 'coat',
              rot=Rz(-s * 13) @ Ry(s * 14), k=0.008)
        S.box(chest, (s * 0.102, 0.503 + br, 0.101), (0.032, 0.024, 0.0035), 0.003, 'coat',
              rot=Rz(-s * 30) @ Ry(s * 18), k=0.008)
        # double-breasted buttons on each front edge
        for yy in (0.1, 0.24):
            S.sph(chest.to((s * (0.09 + 0.125 * yy), yy, 0.127)), 0.0095, 'button')
        # epaulettes
        S.box(chest, (s * 0.12, 0.535 + br + sg * 0.03, -0.01), (0.06, 0.007, 0.024), 0.005, 'coat_dk',
              rot=Rz(s * 16))
        S.sph(chest.to((s * 0.075, 0.548 + br + sg * 0.03, -0.006)), 0.008, 'button')
    shL = chest.to((0.166, 0.50 + br + sg * 0.035, -0.02)); shR = chest.to((-0.166, 0.50 + br + sg * 0.035, -0.02))
    S.cone(chest.to((-0.12, 0.49 + br + sg * 0.02, -0.02)), chest.to((0.12, 0.49 + br + sg * 0.02, -0.02)),
           0.066, 0.066, 'coat', k=0.07)
    S.sph(shL, 0.062, 'coat', k=0.05); S.sph(shR, 0.062, 'coat', k=0.05)
    # turned-up collar, open at the front
    S.tcyl(chest, (0, 0.57 + br, -0.014), (0.1, 0.09), (0.088, 0.078), 0.03, 'coat', shell=0.008,
           clip=((0, 0, -1), -0.035), inmat='lining')
    # belt (left open) with loose ends hanging from the front edges
    for s in (1, -1):
        S.tcyl(chest, (0, 0.085, 0.0), (0.18, 0.136), (0.18, 0.136), 0.022, 'coat_dk', shell=0.004,
               clip=((s, -al, -1), oo + 0.004), clip2=((s, 0, 0), 0.0))
    S.box(chest, (0.072, 0.085, 0.138), (0.016, 0.02, 0.004), 0.002, 'buckle')
    S.decal(chest, 'coat', 'coat_dk', [((1, 0, 0), 0.004), ((-1, 0, 0), 0.004), ((0, 0, 1), -0.03),
                                       ((0, 1, 0), 0.5), ((0, -1, 0), -0.1)])         # back seam

    # --- long coat skirt (open shell hanging from the waist, to just above the knee)
    # panels follow the legs so knees never pierce the cloth: back panel trails the rear thigh,
    # each front panel is kicked forward by its own thigh
    L = p['coatlen']
    top, bot = (0.172, 0.128), (0.255, 0.215)
    hh = (0.2 + L) / 2; cy = 0.2 - hh
    def rad(y):                                     # skirt radii at local height y
        t = (y - (cy - hh)) / (2 * hh)
        return bot[0] + (top[0] - bot[0]) * t, bot[1] + (top[1] - bot[1]) * t
    def ridges(fr, angles):
        # drape folds: soft vertical ridges that widen toward the hem
        for th in angles:
            r0, r1 = math.radians(th), None
            pts = []
            for y in (-0.02, -L + 0.012):
                rx, rz = rad(y)
                pts.append(fr.to((rx * math.sin(r0) * 0.985, y, rz * math.cos(r0) * 0.985)))
            S.cone(pts[0], pts[1], 0.004, 0.017, 'coat', k=0.03)
    back_sw = min(p['lhp'], p['rhp'], 0) * 0.75 + min(p['lhp'] - p['lk'], p['rhp'] - p['rk'], 0) * 0.15
    cfr = Frame(pel.o, pel.M @ Rx(p['lean'] * 0.15) @ swing(back_sw))
    S.tcyl(cfr, (0, cy, 0.004), top, bot, hh, 'coat', shell=0.009, clip=((0, 0, -1), 0.0), inmat='lining')
    ridges(cfr, (118, 146, 166, -118, -146, -166))
    S.decal(cfr, 'coat', 'coat_dk', [((1, 0, 0), 0.004), ((-1, 0, 0), 0.004), ((0, 0, 1), -0.02),
                                     ((0, 1, 0), -0.22)])                              # back vent
    for s, k in ((1, 'l'), (-1, 'r')):
        fsw = min(max(p[k + 'hp'] * 0.9, 0), 50)
        ffr = Frame(pel.o, pel.M @ Rx(p['lean'] * 0.15) @ swing(fsw))
        S.tcyl(ffr, (0, cy, 0.004), top, bot, hh, 'coat', shell=0.009,
               clip=((0, 0, 1), 0.0), clip2=((s, 0.06, 0), 0.064), inmat='lining')
        ridges(ffr, (s * 38, s * 64, s * 86))
        # pocket flap
        th = math.radians(s * 58); rx, rz = rad(-0.1)
        S.box(ffr, (rx * math.sin(th), -0.1, rz * math.cos(th) + 0.004), (0.068, 0.026, 0.006), 0.004, 'coat',
              rot=Ry(s * 58))

    # --- neck + head
    pivot = chest.to((0, 0.632 + br, -0.002))
    hM = chest.M @ Ry(p['hy']) @ Rx(p['hp']) @ Rz(p['hr'])
    head = Frame(pivot + hM @ A(0, 0.092, 0.014), hM, 1.18)
    S.cone(chest.to((0, 0.56 + br, -0.005)), head.to((0, -0.075, -0.018)), 0.064, 0.058, 'skin', k=0.04)
    build_head(S, head, p)

    # --- arms
    for side, k, sh in ((1, 'l', shL), (-1, 'r', shR)):
        build_arm(S, chest, side, sh, p[k + 'sp'], p[k + 'sa'], p[k + 'e'], p[k + 'in'], p[k + 'w'],
                  p[k + 'roll'], p[k + 'hand'], p, k)
    return S

def build_head(S, h, p):
    sk = 'skin'; q = h.s
    # skull and face: soft masses blended together, no hard planes
    S.ell(h, (0, 0.024, -0.012), (0.066, 0.08, 0.086), sk)                          # cranium
    S.ell(h, (0, -0.028, 0.02), (0.057, 0.07, 0.07), sk, k=0.035)                   # face mass
    S.ell(h, (0, -0.07, 0.026), (0.05, 0.03, 0.056), sk, k=0.03)                    # jaw
    S.ell(h, (0, -0.088, 0.054), (0.025, 0.02, 0.022), sk, k=0.02)                  # chin
    for s in (1, -1):
        S.ell(h, (s * 0.04, -0.014, 0.048), (0.017, 0.012, 0.018), sk, k=0.03)      # cheekbone
        S.ell(h, (s * 0.062, -0.006, -0.008), (0.011, 0.024, 0.016), sk, k=0.008, rot=Ry(s * 18))   # ear
    S.cone(h.to((-0.034, 0.03, 0.072)), h.to((0.034, 0.03, 0.072)), 0.008 * q, 0.008 * q, sk, k=0.02)   # brow ridge
    S.cone(h.to((0, 0.02, 0.083)), h.to((0, -0.02, 0.097)), 0.0068 * q, 0.0092 * q, sk, k=0.012)        # nose
    S.ell(h, (0, -0.023, 0.091), (0.0125, 0.0075, 0.0095), sk, k=0.01)              # nose tip / nostrils
    for s in (1, -1):
        S.ell(h, (s * 0.03, 0.009, 0.079), (0.0125, 0.0075, 0.008), sk, op=1, k=0.009)   # eye socket
    if p['mouth'] > 0:
        mo = p['mouth']
        S.ell(h, (0, -0.055, 0.084), (0.017, 0.004 + 0.007 * mo, 0.02), sk, op=1, k=0.004)
        S.ell(h, (0, -0.055, 0.07), (0.018, 0.013, 0.01), 'mouthin')
    else:
        S.cone(h.to((-0.017, -0.054, 0.083)), h.to((0.017, -0.054, 0.083)), 0.0022 * q, 0.0022 * q, sk, op=1, k=0.004)
    for s in (1, -1):
        ex = s * 0.03
        S.sph(h.to((ex, 0.008, 0.068)), 0.011 * q, 'eyew')
        bl = p['blink']
        S.ell(h, (ex, 0.0158 - 0.009 * bl, 0.07), (0.0128, 0.0052 + 0.004 * bl, 0.0118), sk, k=0.003)   # upper lid
        S.ell(h, (ex, 0.0005, 0.071), (0.011, 0.0035, 0.0105), sk, k=0.003)                         # lower lid
        S.decal(h, 'eyew', 'iris', [((0, 0, -1), -(0.068 + 0.0074)), ((1, 0, 0), ex + 0.0075), ((-1, 0, 0), -ex + 0.0075)])
        S.decal(h, 'iris', 'pupil', [((0, 0, -1), -(0.068 + 0.0106))])
        S.decal(h, sk, 'brow', [((0, 1, 0), 0.0285), ((0, -1, 0), -0.0215), ((s, 0, 0), ex * s + 0.017),
                                ((-s, 0, 0), -ex * s + 0.013), ((0, 0, -1), -0.05)], feather=0.0025)
    S.decal(h, sk, 'lips', [((1, 0, 0), 0.018), ((-1, 0, 0), 0.018), ((0, 1, 0), -0.049), ((0, -1, 0), 0.062), ((0, 0, -1), -0.065)], feather=0.004)
    # stubble on the lower face and jaw
    if p['stubble']:
        S.decal(h, sk, 'stubble', [((0, 1, 0.25), -0.03), ((0, 0, -1), 0.005)], feather=0.012)
        S.decal(h, sk, 'stubble', [((0, 1, 0), -0.05), ((0, 0, -1), 0.03)], feather=0.012)
    if p['mustache']:
        S.ell(h, (0, -0.036, 0.09), (0.013, 0.0055, 0.006), 'hair', k=0.003)          # toothbrush mustache
    if p['beard']:                                                                   # full, trimmed, under the lip
        S.ell(h, (0, -0.075, 0.034), (0.064, 0.046, 0.066), 'hair', k=0.012, clip=h.plane((0, -1, 0), 0.058))
        S.ell(h, (0, -0.036, 0.088), (0.02, 0.006, 0.008), 'hair', k=0.004)
        for s in (1, -1):
            S.ell(h, (s * 0.052, -0.04, 0.02), (0.014, 0.04, 0.04), 'hair', k=0.012)
    if p['headset']:                                                                 # band over the top, mic at the mouth
        pts = [h.to((0.072 * math.cos(a), 0.012 + 0.098 * math.sin(a), -0.01)) for a in np.linspace(0, math.pi, 9)]
        for a, b in zip(pts, pts[1:]):
            S.cyl(a, b, 0.006 * q, 'phone')
        S.ell(h, (-0.074, -0.004, -0.004), (0.012, 0.028, 0.026), 'phone')
        S.cyl(h.to((-0.074, -0.02, 0.01)), h.to((-0.035, -0.05, 0.085)), 0.0035 * q, 'phone')
        S.sph(h.to((-0.032, -0.052, 0.088)), 0.008 * q, 'phone')
    if p['earring']:
        es = 1 if p['earring'] == 'l' else -1
        S.sph(h.to((es * 0.066, -0.032, -0.004)), 0.0075 * q, 'gold')                  # one gold stud
    # short salt-and-pepper hair, a little swept back, grey at the temples
    style = p['hair']
    if style == 'bald':                                                              # a fringe round the back
        S.ell(h, (0, -0.002, -0.06), (0.064, 0.042, 0.04), 'hair', k=0.02)
        for s in (1, -1):
            S.ell(h, (s * 0.058, 0.0, -0.026), (0.013, 0.026, 0.04), 'hair', k=0.016)
        return
    S.decal(h, sk, 'hair', [((0, -1, 0.7), 0.004), ((0, -1, 0), -0.035)], feather=0.006)
    if style == 'short_crop':                                                        # close-cropped, tight to the skull
        S.ell(h, (0, 0.03, -0.014), (0.07, 0.082, 0.09), 'hair', k=0.004, clip=h.plane((0, 0.944, -0.33), 0.0))
        return
    S.ell(h, (0, 0.05, -0.012), (0.069, 0.06, 0.09), 'hair', k=0.018)               # top mass
    S.ell(h, (0, 0.074, 0.03), (0.054, 0.032, 0.05), 'hair', k=0.022, rot=Rx(-12))  # front lift
    S.ell(h, (0, 0.012, -0.052), (0.066, 0.066, 0.054), 'hair', k=0.02)             # back
    for s in (1, -1):
        S.ell(h, (s * 0.057, 0.026, -0.014), (0.014, 0.04, 0.062), 'hair', k=0.018)  # sides
        if style == 'short':
            S.decal(h, 'hair', 'skin', [((-s, 0, 0), -0.05), ((0, 1, 0), 0.058), ((0, 0, -1), -0.052)], feather=0.008)   # receding temples
        S.decal(h, 'hair', 'hairgrey', [((-s, 0, 0), -0.048), ((0, 1, 0), 0.048), ((0, -1, 0), 0.004),
                                        ((0, 0, 1), 0.05), ((0, 0, -1), 0.035)], feather=0.014)        # grey at the temples
    if style in ('bun', 'bun_pencil'):                                               # pinned up
        S.sph(h.to((0, 0.06, -0.078)), 0.036 * q, 'hair', k=0.012)
        if style == 'bun_pencil':
            S.cone(h.to((-0.06, 0.1, -0.07)), h.to((0.05, 0.05, -0.09)), 0.004 * q, 0.004 * q, 'card')
    elif style in ('long', 'long_side'):                                             # to the shoulders
        S.ell(h, (0, -0.03, -0.05), (0.072, 0.11, 0.05), 'hair', k=0.025)
        for s in (1, -1):
            S.ell(h, (s * 0.06, -0.03, -0.01), (0.018, 0.09, 0.05), 'hair', k=0.02)
        if style == 'long_side':                                                     # swept down over the left ear
            S.ell(h, (0.05, -0.02, 0.04), (0.024, 0.1, 0.045), 'hair', k=0.02, rot=Rz(-8))
            S.ell(h, (0.03, 0.06, 0.06), (0.04, 0.02, 0.035), 'hair', k=0.02, rot=Rz(-20))
    elif style == 'derby':                                                           # a bowler hat
        S.ell(h, (0, 0.078, -0.008), (0.07, 0.052, 0.078), 'cap', k=0.006)
        S.tcyl(h, (0, 0.042, -0.008), (0.098, 0.106), (0.098, 0.106), 0.004, 'cap')
    elif style == 'hood':                                                            # a hoodie's hood, up
        S.ell(h, (0, 0.03, -0.018), (0.088, 0.104, 0.104), 'coat', k=0.01, clip=h.plane((0, 0, -1), -0.045))
        S.ell(h, (0, -0.04, -0.03), (0.08, 0.06, 0.08), 'coat', k=0.02, clip=h.plane((0, 0, -1), -0.03))
    elif style == 'cap':                                                             # patrol cap
        S.ell(h, (0, 0.062, -0.006), (0.075, 0.042, 0.092), 'cap', k=0.01)
        S.box(h, (0, 0.05, 0.088), (0.06, 0.004, 0.035), 0.003, 'cap', rot=Rx(-12))
        S.ell(h, (0, -0.02, -0.07), (0.05, 0.05, 0.03), 'hair', k=0.02)            # tucked-up hair

def build_arm(S, chest, side, sh, sp, sa, el, inward, wr, roll, hand, p, key):
    s = side
    L = chest.M @ swing(sp) @ Rz(s * sa)
    elbow = sh + 0.30 * (L @ A(0, -1, 0))
    Lf = L @ Ry(-s * inward) @ swing(el)
    wrist = elbow + 0.27 * (Lf @ A(0, -1, 0))
    sl = p['sleeves']
    S.cone(sh, elbow, 0.064, 0.055, sl, k=0.03)
    S.cone(elbow, wrist, 0.055, 0.05, sl, k=0.014)
    S.sph(elbow + (L @ A(0, 0, -1)) * 0.012, 0.05, sl, k=0.03)                     # elbow bunching
    fd = Lf @ A(0, -1, 0)
    S.cone(wrist - fd * 0.075, wrist - fd * 0.01, 0.055, 0.054, sl)                # sleeve end
    if sl == 'coat':
        S.cone(wrist - fd * 0.07, wrist - fd * 0.05, 0.058, 0.058, 'coat_dk')      # cuff strap
    S.cone(wrist - fd * 0.03, wrist + fd * 0.004, 0.037, 0.036, 'shirt')            # shirt cuff
    if s == 1:
        S.cone(wrist + fd * 0.005, wrist + fd * 0.017, 0.031, 0.031, 'steel')       # watch
    Lh = Lf @ swing(wr) @ Ry(s * roll)
    hf = Frame(wrist, Lh)
    S.cone(wrist - fd * 0.01, wrist + fd * 0.03, 0.028, 0.026, 'skin', k=0.01)
    S.ell(hf, (0, -0.06, 0.0), (0.017, 0.05, 0.041), 'skin', k=0.015)               # palm
    if hand == 'fist':
        S.ell(hf, (-s * 0.01, -0.105, 0.0), (0.024, 0.03, 0.04), 'skin', k=0.012)
    elif hand == 'open':
        S.ell(hf, (0, -0.135, 0.0), (0.012, 0.05, 0.04), 'skin', k=0.012)
    elif hand == 'hold':
        S.ell(hf, (-s * 0.016, -0.11, 0.0), (0.02, 0.034, 0.04), 'skin', k=0.012, rot=Rz(s * 25))
    else:  # relaxed, fingers gently curled
        S.ell(hf, (-s * 0.008, -0.122, 0.004), (0.018, 0.046, 0.04), 'skin', k=0.012, rot=Rz(s * 14))
    S.cone(hf.to((-s * 0.008, -0.03, 0.032)), hf.to((-s * 0.02, -0.085, 0.045)), 0.0125, 0.0095, 'skin', k=0.008)
    grip = hf.to((-s * 0.03, -0.1, 0.0))
    props = p['props']
    cf = Frame(grip, chest.M)
    if ('box', key) in props:
        S.box(cf, (0, 0, 0.0), (0.05, 0.035, 0.06), 0.004, 'card')
        S.box(cf, (0, 0.036, 0.0), (0.052, 0.002, 0.062), 0.001, 'card')
    if ('notebook', key) in props:
        nf = Frame(grip, chest.M @ Rx(-55))
        S.box(nf, (0, 0.0, 0.0), (0.05, 0.068, 0.008), 0.003, 'leather')
        S.box(nf, (0, 0.002, 0.004), (0.046, 0.064, 0.006), 0.001, 'paper')
    if ('pen', key) in props:
        S.cone(hf.to((-s * 0.02, -0.07, 0.03)), hf.to((-s * 0.03, -0.15, 0.06)), 0.004, 0.003, 'pen')
    if ('torch', key) in props:
        S.cone(hf.to((-s * 0.02, -0.08, -0.06)), hf.to((-s * 0.02, -0.08, 0.12)), 0.016, 0.022, 'torch')
        S.cyl(hf.to((-s * 0.02, -0.08, 0.12)), hf.to((-s * 0.02, -0.08, 0.125)), 0.02, 'torch_lit')
    if ('pipe', key) in props:                                                       # a briar pipe
        S.cyl(hf.to((-s * 0.02, -0.1, 0.03)), hf.to((-s * 0.02, -0.1, 0.13)), 0.006, 'pipe')
        S.cone(hf.to((-s * 0.02, -0.1, 0.13)), hf.to((-s * 0.02, -0.05, 0.14)), 0.016, 0.019, 'pipe')
    if ('umbrella', key) in props:                                                   # shaft up past the head, canopy
        top = grip + chest.M @ A(0, 0.78, 0.02)
        S.cyl(grip - chest.M @ A(0, 0.08, 0), top, 0.008, 'umbrella')
        S.tcyl(Frame(top - chest.M @ A(0, 0.1, 0), chest.M), (0, 0, 0), (0.03, 0.03), (0.5, 0.5), 0.09, 'umbrella')
    if ('glass', key) in props:                                                      # a tumbler of water
        gf = Frame(grip + chest.M @ A(0, 0.02, 0.0), chest.M)
        S.tcyl(gf, (0, 0, 0), (0.036, 0.036), (0.03, 0.03), 0.055, 'glass_c')
        S.tcyl(gf, (0, -0.012, 0), (0.033, 0.033), (0.029, 0.029), 0.04, 'water_c')
    if ('clipboard', key) in props:
        cbf = Frame(grip + chest.M @ A(0, 0.03, 0.04), chest.M @ Rx(-60))
        S.box(cbf, (0, 0, 0), (0.11, 0.15, 0.005), 0.004, 'card')
        S.box(cbf, (0, -0.01, 0.006), (0.1, 0.13, 0.002), 0.001, 'paper')
        S.box(cbf, (0, 0.14, 0.01), (0.03, 0.012, 0.008), 0.003, 'steel')
    if ('book', key) in props:                                                       # a pocket Bible, open
        bkf = Frame(grip + chest.M @ A(0, 0.02, 0.05), chest.M @ Rx(-50))
        S.box(bkf, (0, 0, 0), (0.07, 0.05, 0.008), 0.003, 'leather')
        S.box(bkf, (0, 0, 0.007), (0.066, 0.046, 0.004), 0.001, 'paper')
    if ('phone', key) in props:                                                      # held out, screen lit
        pf = Frame(grip + chest.M @ A(0, 0.04, 0.03), chest.M @ Rx(-70))
        S.box(pf, (0, 0, 0), (0.036, 0.072, 0.005), 0.004, 'phone')
        S.box(pf, (0, 0, 0.0052), (0.032, 0.066, 0.001), 0.0, 'screen')
    if ('badge', key) in props:
        bf = Frame(grip + chest.M @ A(0, 0.02, 0.03), chest.M)
        S.box(bf, (0, 0, 0), (0.04, 0.055, 0.007), 0.004, 'leather')
        S.ell(bf, (0, 0.008, 0.008), (0.026, 0.032, 0.004), 'gold')
        S.ell(bf, (0, -0.03, 0.008), (0.012, 0.012, 0.004), 'gold')

# ---------------------------------------------------------------- render
