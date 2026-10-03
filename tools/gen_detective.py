"""Pixel-art detective sprite sheet: procedural shapes rasterised at native resolution,
three-tone shading per part, coloured selective outlines."""
import math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FW, FH = 96, 136
GROUND = 131

def rgb(*c): return tuple(c) + (255,)
# light, base, shadow, outline
P = {
    'skin':  (rgb(238, 190, 152), rgb(214, 160, 122), rgb(172, 114, 86), rgb(96, 52, 40)),
    'skinF': (rgb(198, 146, 112), rgb(178, 126, 96), rgb(144, 96, 72), rgb(84, 46, 36)),
    'hair':  (rgb(98, 76, 62), rgb(68, 52, 44), rgb(46, 34, 30), rgb(24, 18, 16)),
    'coat':  (rgb(220, 186, 138), rgb(188, 150, 106), rgb(146, 110, 76), rgb(70, 46, 32)),
    'coatF': (rgb(170, 134, 96), rgb(150, 116, 82), rgb(118, 88, 62), rgb(62, 40, 28)),
    'lining': (rgb(124, 80, 62), rgb(100, 62, 50), rgb(78, 46, 38), rgb(44, 26, 22)),
    'vest':  (rgb(72, 88, 126), rgb(50, 62, 96), rgb(36, 44, 72), rgb(18, 20, 36)),
    'shirt': (rgb(208, 228, 244), rgb(170, 200, 230), rgb(128, 160, 200), rgb(52, 64, 92)),
    'tie':   (rgb(166, 100, 62), rgb(132, 76, 46), rgb(98, 54, 32), rgb(50, 26, 16)),
    'pants': (rgb(70, 82, 116), rgb(48, 58, 88), rgb(34, 40, 64), rgb(16, 18, 32)),
    'pantsF': (rgb(52, 62, 92), rgb(40, 48, 74), rgb(30, 36, 56), rgb(14, 16, 28)),
    'shoe':  (rgb(150, 88, 56), rgb(112, 60, 38), rgb(80, 40, 26), rgb(36, 18, 12)),
    'box':   (rgb(206, 166, 110), rgb(176, 134, 84), rgb(136, 98, 58), rgb(66, 44, 24)),
    'paper': (rgb(246, 240, 220), rgb(226, 220, 196), rgb(190, 182, 156), rgb(80, 70, 56)),
    'leather': (rgb(92, 60, 44), rgb(68, 42, 30), rgb(48, 28, 20), rgb(24, 12, 8)),
}
C = dict(eye=rgb(30, 24, 26), white=rgb(226, 218, 206), brow=rgb(44, 32, 28), mouth=rgb(132, 70, 60),
         stub=rgb(176, 124, 98), stub2=rgb(156, 108, 86), grey=rgb(150, 144, 138), greyD=rgb(112, 106, 102),
         gold=rgb(226, 186, 76), goldH=rgb(255, 240, 160), btn=rgb(120, 82, 52), belt=rgb(80, 48, 30),
         buckle=rgb(200, 186, 150), ink=rgb(22, 20, 26), mouthin=rgb(70, 26, 26), steel=rgb(190, 192, 198))

R = lambda p: (int(round(p[0])), int(round(p[1])))
def vec(a, L):
    r = math.radians(a); return (math.sin(r) * L, math.cos(r) * L)
def add(p, q): return (p[0] + q[0], p[1] + q[1])

def sh(a, dx, dy):  # b[y,x] = a[y+dy, x+dx]
    b = np.zeros_like(a); H, W = a.shape
    b[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)] = a[max(0, dy):H - max(0, -dy), max(0, dx):W - max(0, -dx)]
    return b

class Frame:
    def __init__(self, lx=1):
        self.arr = np.zeros((FH, FW, 4), np.uint8); self.lx = lx
    def part(self, fn, mat, sw=2, outline=True, flat=False):
        m = Image.new('L', (FW, FH), 0); fn(ImageDraw.Draw(m))
        a = np.array(m) > 0
        if not a.any(): return a
        L, B, S, O = P[mat]
        out = self.arr
        out[a] = B
        if not flat:
            s = -2 * self.lx // 2 * sw  # shadow side opposite the light
            shadow = a & ~sh(a, s, 0) | a & ~sh(a, 0, 2)
            hl = a & ~sh(a, self.lx, -1) & ~shadow
            out[shadow] = S; out[hl] = L
        if outline:
            d = a.copy()
            d[1:] |= a[:-1]; d[:-1] |= a[1:]; d[:, 1:] |= a[:, :-1]; d[:, :-1] |= a[:, 1:]
            out[d & ~a] = O
        return a
    def px(self, p, c):
        x, y = R(p)
        if 0 <= x < FW and 0 <= y < FH: self.arr[y, x] = c
    def line(self, p0, p1, c):
        x0, y0 = R(p0); x1, y1 = R(p1); n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1): self.px((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n), c)
    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1): self.px((x, y), c)
    def img(self): return Image.fromarray(self.arr, 'RGBA')

def cap(d, p0, p1, w):
    p0, p1 = R(p0), R(p1)
    d.line([p0, p1], fill=255, width=w)
    r = (w - 1) / 2
    for x, y in (p0, p1): d.ellipse([x - r, y - r, x + r, y + r], fill=255)
def poly(d, pts): d.polygon([R(p) for p in pts], fill=255)

# ======================================================================== side view (faces right)
TH, SH, UA, FA = 26, 26, 17, 15
SIDE = dict(lean=0, bt=-3, bk=4, ft=4, fk=4, bu=-4, bf=4, fu=4, ff=10, mouth=0, blink=0,
            b=0, hdy=0, hold=None, pen=False, coat=34)

def side(**kw):
    p = dict(SIDE); p.update(kw)
    x0, b = 44, p['b']
    def drop(t, k): return vec(t, TH)[1] + vec(t - k, SH)[1]
    hy = GROUND - 4 - max(drop(p['bt'], p['bk']), drop(p['ft'], p['fk']))
    l = math.radians(p['lean'])
    fwd = (math.cos(l), math.sin(l)); up = (math.sin(l), -math.cos(l))
    def T(u, v): return (x0 + u * fwd[0] + v * up[0], hy + u * fwd[1] + v * up[1])
    F = Frame(lx=1)

    def legpts(t, k, hx):
        knee = add((hx, hy), vec(t, TH)); ank = add(knee, vec(t - k, SH)); return knee, ank
    def leg(t, k, hx, far):
        def f(d):
            knee, ank = legpts(t, k, hx)
            cap(d, (hx, hy), knee, 10); cap(d, knee, ank, 8)
        def shoe(d):
            knee, ank = legpts(t, k, hx); ax, ay = R(ank)
            d.rectangle([ax - 4, ay - 1, ax + 7, ay + 3], fill=255)
            d.rectangle([ax + 6, ay + 1, ax + 9, ay + 3], fill=255)
        F.part(f, 'pantsF' if far else 'pants')
        F.part(shoe, 'shoe', sw=1)
    def arm_pts(u, fa):
        s = T(0, 31 + b); e = add(s, vec(u, UA)); h = add(e, vec(fa, FA + 2)); return s, e, h
    def arm(u, fa, far):
        s, e, h = arm_pts(u, fa)
        def sl(d):
            cap(d, s, e, 8); cap(d, e, add(e, vec(fa, FA - 2)), 8)
        def cuff(d):
            c0 = add(e, vec(fa, FA - 5)); c1 = add(e, vec(fa, FA - 1)); cap(d, c0, c1, 9)
        def hand(d):
            x, y = R(h); d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=255)
        F.part(sl, 'coatF' if far else 'coat')
        F.part(cuff, 'coatF' if far else 'coat', sw=1)
        F.part(hand, 'skinF' if far else 'skin', sw=1)
        return h

    # back arm and legs
    bh = arm(p['bu'], p['bf'], True)
    if p['pen']:
        F.line(bh, add(bh, (3, -5)), C['ink'])
    leg(p['bt'], p['bk'], x0 - 2, True)
    leg(p['ft'], p['fk'], x0 + 2, False)

    # coat skirt: back edge trails the rear thigh, front edge is kicked by the front thigh
    L = p['coat']
    ba = min(p['bt'], p['ft'], 0) * 0.6 + p['lean'] * 0.25
    fa = min(max(p['bt'], p['ft'], 0) * 0.7, 55) + p['lean'] * 0.2
    wb, wf = T(-10.5, 2), T(9.5, 2)
    hb = add(add((x0 - 11, hy), vec(ba, L)), (-2, 0))
    hf = add(add((x0 + 9, hy), vec(fa, L)), (2, 0))
    hm = ((hb[0] + hf[0]) / 2, max(hb[1], hf[1]) + 1)
    F.part(lambda d: poly(d, [wb, hb, hm, hf, wf]), 'coat')
    # skirt details: pocket flap, side seam fold
    pk = add(T(1, -8), vec(fa * 0.5, 0))
    F.line(add(pk, (0, 0)), add(pk, (6, 0)), P['coat'][3])
    F.line(add(T(-3, 0), (0, 2)), add(hb, (6, -3)), P['coat'][2])

    # upper coat
    def torso(d):
        poly(d, [T(-10, 0), T(-10.5, 18), T(-9, 29 + b), T(-5, 34 + b), T(3, 34.5 + b), T(8, 31 + b),
                 T(10, 22), T(9.5, 8), T(9.5, 0)])
    F.part(torso, 'coat')
    # open front: waistcoat, shirt, tie, lapel
    F.part(lambda d: poly(d, [T(5, 33 + b), T(8.5, 30 + b), T(10, 21), T(9.5, 5), T(7.5, 5), T(7, 22)]), 'vest', sw=1)
    F.part(lambda d: poly(d, [T(5, 33.5 + b), T(8.5, 31 + b), T(9.3, 25), T(7, 27)]), 'shirt', sw=1, outline=False)
    F.line(T(9.0, 30 + b), T(9.6, 20), P['tie'][1])
    F.px(T(8.6, 12), C['btn']); F.px(T(8.9, 17), C['btn'])
    F.line(T(4, 34 + b), T(7, 23), P['coat'][3])                 # lapel roll line
    F.line(T(4.5, 33 + b), T(6.5, 24), P['coat'][0])
    F.line(T(-3, 4), T(-4, 26), P['coat'][2])                    # back fold
    # popped collar behind the neck
    F.part(lambda d: poly(d, [T(-5, 33 + b), T(-4, 40 + b), T(0, 41 + b), T(2, 35 + b)]), 'coat', sw=1)

    # neck and head
    cx, cy = R(T(2, 43 + b)); cy += p['hdy']; cx += 1 if p['hdy'] > 0 else 0
    F.part(lambda d: cap(d, T(0.5, 33 + b), (cx - 1, cy + 6), 7), 'skin', sw=2)
    def head(d):
        d.ellipse([cx - 8, cy - 10, cx + 7, cy + 9], fill=255)
        d.rectangle([cx + 1, cy + 3, cx + 6, cy + 10], fill=255)      # jaw
        d.rectangle([cx + 7, cy - 2, cx + 9, cy + 2], fill=255)      # nose
        d.point((cx + 8, cy + 3), fill=255)
        d.rectangle([cx + 6, cy + 6, cx + 7, cy + 9], fill=255)      # chin
    F.part(head, 'skin', sw=3)
    def hair(d):
        poly(d, [(cx - 8, cy + 3), (cx - 9, cy - 4), (cx - 6, cy - 10), (cx - 1, cy - 12), (cx + 5, cy - 11),
                 (cx + 8, cy - 8), (cx + 8, cy - 6), (cx + 4, cy - 7), (cx + 1, cy - 6), (cx - 1, cy - 3),
                 (cx - 2, cy + 1), (cx - 4, cy + 3), (cx - 6, cy + 4)])
    F.part(hair, 'hair', sw=2)
    # strands swept back
    for (a0, a1) in (((cx + 4, cy - 10), (cx - 3, cy - 10)), ((cx + 6, cy - 8), (cx - 2, cy - 7)), ((cx, cy - 5), (cx - 6, cy - 4))):
        F.line(a0, a1, P['hair'][0])
    # grey temple + sideburn
    for q in ((cx - 2, cy - 2), (cx - 2, cy - 1), (cx - 1, cy - 3), (cx - 3, cy), (cx - 3, cy + 1)): F.px(q, C['grey'])
    F.px((cx - 2, cy), C['greyD'])
    # ear
    F.rect(cx - 4, cy - 1, cx - 2, cy + 3, P['skin'][2]); F.px((cx - 3, cy), P['skin'][0])
    # face
    F.line((cx + 3, cy - 4), (cx + 7, cy - 4), C['brow']); F.px((cx + 3, cy - 3), C['brow'])
    if p['blink']:
        F.line((cx + 4, cy - 2), (cx + 6, cy - 2), P['skin'][3])
    else:
        F.px((cx + 5, cy - 2), C['eye']); F.px((cx + 5, cy - 1), C['eye']); F.px((cx + 6, cy - 2), C['white'])
    F.px((cx + 5, cy), P['skin'][2]); F.px((cx + 6, cy), P['skin'][2])           # bags
    F.line((cx + 9, cy + 1), (cx + 9, cy + 2), P['skin'][2])
    F.px((cx + 7, cy + 2), P['skin'][2])                                        # nostril
    for y in range(cy + 3, cy + 11):
        for x in range(cx - 1, cx + 9):
            if (x + y) % 2 == 0 and F.arr[y, x, 3] and tuple(F.arr[y, x]) in (P['skin'][1], P['skin'][2]) \
               and (y > cy + 4 or x < cx + 3):
                F.px((x, y), C['stub'] if tuple(F.arr[y, x]) == P['skin'][1] else C['stub2'])
    if p['mouth']:
        F.rect(cx + 6, cy + 5, cx + 7, cy + 6, C['mouthin'])
    else:
        F.line((cx + 5, cy + 6), (cx + 7, cy + 6), C['mouth'])
    F.px((cx + 3, cy + 1), P['skin'][2])                                        # cheek line

    # front arm, props
    s, e, h = arm_pts(p['fu'], p['ff'])
    if p['hold'] == 'notebook':
        hx, hy2 = R(h)
        F.part(lambda d: d.rectangle([hx - 1, hy2 - 9, hx + 6, hy2], fill=255), 'paper', sw=1)
        for i in range(3): F.line((hx + 1, hy2 - 7 + i * 2), (hx + 5, hy2 - 7 + i * 2), P['paper'][2])
    arm(p['fu'], p['ff'], False)
    if p['hold'] == 'box':
        hx, hy2 = R(h)
        F.part(lambda d: d.rectangle([hx - 4, hy2 - 8, hx + 5, hy2 - 1], fill=255), 'box', sw=1)
        F.line((hx - 3, hy2 - 6), (hx + 4, hy2 - 6), P['box'][2])
        F.part(lambda d: d.ellipse([hx - 3, hy2 - 3, hx + 3, hy2 + 3], fill=255), 'skin', sw=1)
    return F.img()

# ======================================================================== front / back
K = 1.45  # scale of arm offsets
def front(ll=0, rl=0, ld=0, rd=0, lhand=None, rhand=None, mouth=0, blink=0, turn=0,
          shrug=0, back=False, badge=False, hdy=0, bob=0):
    hy = GROUND - 4 - 52 + bob
    sy = hy - 36
    F = Frame(lx=-1)
    cx = 48
    # legs (nearer one drawn last)
    legs = sorted([(cx - 5, ll, ld), (cx + 5, rl, rd)], key=lambda t: t[2])
    for hx, lift, dep in legs:
        ay = hy + 52 - lift * 7 + dep
        ky = hy + 26 - lift * 4
        kx = hx + (1 if hx > cx else -1) * lift
        F.part(lambda d: (cap(d, (hx, hy), (kx, ky), 10), cap(d, (kx, ky), (hx, ay), 9)), 'pants')
        F.line((hx + (3 if hx > cx else -3), hy + 30), (hx + (3 if hx > cx else -3), ay - 5), P['pants'][2])
        ayi = int(round(ay))
        def shoe(d, hx=hx, ayi=ayi):
            d.rectangle([hx - 4, ayi - 1, hx + 4, ayi + 3], fill=255)
            d.rectangle([hx - 3, ayi + 4, hx + 3, ayi + 4], fill=255)
        F.part(shoe, 'shoe', sw=1)
        if not back: F.line((hx - 2, ayi), (hx + 1, ayi), P['shoe'][0])

    s = shrug * 3
    hem = hy + 34
    # back panel / lining seen between the legs
    if not back:
        F.part(lambda d: poly(d, [(cx - 6, hy + 4), (cx + 6, hy + 4), (cx + 9, hem - 1), (cx - 9, hem - 1)]), 'lining', sw=1)
        for hx, lift, dep in legs:   # legs in front of lining
            ay = hy + 52 - lift * 7 + dep; ky = hy + 26 - lift * 4
            kx = hx + (1 if hx > cx else -1) * lift
            F.part(lambda d: (cap(d, (hx, hy + 6), (kx, ky), 10), cap(d, (kx, ky), (hx, ay - 2), 9)), 'pants')
        # belt and seat
        F.part(lambda d: d.rectangle([cx - 8, hy - 3, cx + 8, hy + 6], fill=255), 'pants', sw=1)
        F.rect(cx - 8, hy - 3, cx + 8, hy - 2, C['belt']); F.rect(cx - 1, hy - 3, cx + 1, hy - 2, C['buckle'])
    # coat skirt panels; each lifts with its leg
    for side_, lift in ((-1, ll), (1, rl)):
        x_in = cx + side_ * (3 if not back else 0)
        x_w = cx + side_ * 16.5
        x_h = cx + side_ * 21
        x_hi = cx + side_ * (7 if not back else 0)
        hl = hem - lift * 3
        F.part(lambda d, a=(x_in, x_w, x_h, x_hi, hl): poly(d, [(a[0], hy - 2), (a[1], hy - 2), (a[2], a[4]), (a[3], a[4])]), 'coat')
        if not back:
            F.line((cx + side_ * 9, hy + 13), (cx + side_ * 15, hy + 13), P['coat'][3])   # pocket flap
            F.line((cx + side_ * 9, hy + 14), (cx + side_ * 15, hy + 14), P['coat'][2])
    if back:
        F.line((cx, hy + 14), (cx, hem - 1), P['coat'][3])  # vent
    # upper coat
    def torso(d):
        poly(d, [(cx - 17, sy + 4 - s), (cx - 12, sy - s), (cx + 12, sy - s), (cx + 17, sy + 4 - s),
                 (cx + 16, hy - 1), (cx - 16, hy - 1)])
    F.part(torso, 'coat', sw=3)
    if back:
        F.line((cx, sy + 4), (cx, hy - 1), P['coat'][2])
        F.line((cx - 10, sy + 14), (cx - 6, hy - 2), P['coat'][2])
        F.line((cx + 10, sy + 14), (cx + 6, hy - 2), P['coat'][2])
    else:
        F.part(lambda d: poly(d, [(cx - 7, sy - s), (cx + 7, sy - s), (cx + 4, hy - 1), (cx - 4, hy - 1)]), 'vest', sw=1)
        F.part(lambda d: poly(d, [(cx - 5, sy - s), (cx + 5, sy - s), (cx, sy + 13)]), 'shirt', sw=1, outline=False)
        F.part(lambda d: poly(d, [(cx - 1, sy + 1 - s), (cx + 1, sy + 1 - s), (cx + 2, sy + 11), (cx, sy + 13), (cx - 2, sy + 11)]), 'tie', sw=1)
        F.rect(cx - 1, sy - s, cx + 1, sy + 1 - s, P['tie'][2])
        for yy in range(sy + 16, hy - 2, 5): F.px((cx, yy), C['btn'])
        for sd in (-1, 1):  # lapels folding back
            F.part(lambda d, sd=sd: poly(d, [(cx + sd * 7, sy - s), (cx + sd * 12, sy + 1 - s), (cx + sd * 10, sy + 14), (cx + sd * 6, sy + 20)]), 'coat', sw=1)
            F.px((cx + sd * 8, hy - 8), C['btn'])
            F.line((cx + sd * 9, sy + 9), (cx + sd * 12, sy + 9), P['coat'][3])  # breast welt
    # collar up around the neck
    for sd in (-1, 1):
        F.part(lambda d, sd=sd: poly(d, [(cx + sd * 6, sy - 6 - s), (cx + sd * 10, sy - 4 - s), (cx + sd * 12, sy + 1 - s), (cx + sd * 7, sy + 1 - s)]), 'coat', sw=1)

    # head
    hc_x, hc_y = cx, sy - 13 + hdy
    t = turn * 2
    F.part(lambda d: d.rectangle([cx - 4, sy - 6 - s, cx + 4, sy - s], fill=255), 'skin', sw=1)
    def head(d):
        d.ellipse([hc_x - 8, hc_y - 10, hc_x + 8, hc_y + 9], fill=255)
        d.rectangle([hc_x - 6, hc_y + 3, hc_x + 6, hc_y + 10], fill=255)
        if turn != -1 or back: d.rectangle([hc_x - 10, hc_y - 2, hc_x - 8, hc_y + 3], fill=255)
        if turn != 1 or back: d.rectangle([hc_x + 8, hc_y - 2, hc_x + 10, hc_y + 3], fill=255)
    F.part(head, 'skin', sw=3)
    def hair(d):
        if back:
            poly(d, [(hc_x - 9, hc_y + 4), (hc_x - 9, hc_y - 5), (hc_x - 5, hc_y - 11), (hc_x + 5, hc_y - 11),
                     (hc_x + 9, hc_y - 5), (hc_x + 9, hc_y + 4), (hc_x + 5, hc_y + 7), (hc_x - 5, hc_y + 7)])
        else:
            poly(d, [(hc_x - 9, hc_y + 1), (hc_x - 9, hc_y - 5), (hc_x - 5, hc_y - 11), (hc_x + 5, hc_y - 12),
                     (hc_x + 9, hc_y - 5), (hc_x + 9, hc_y + 1), (hc_x + 7, hc_y - 5 + 0), (hc_x + 2 + t, hc_y - 7),
                     (hc_x - 3 + t, hc_y - 6), (hc_x - 7, hc_y - 5)])
    F.part(hair, 'hair', sw=2)
    for xx in range(-5, 6, 3):
        F.line((hc_x + xx, hc_y - 10), (hc_x + xx + (0 if back else 1), hc_y - (4 if back else 7)), P['hair'][0])
    for sd in (-1, 1):  # greying temples
        F.px((hc_x + sd * 9, hc_y - 2), C['grey']); F.px((hc_x + sd * 9, hc_y - 3), C['grey']); F.px((hc_x + sd * 8, hc_y - 4), C['greyD'])
    if not back:
        ex1, ex2 = hc_x - 4 + t, hc_x + 3 + t
        for ex in (ex1, ex2):
            F.line((ex - 1, hc_y - 3), (ex + 2, hc_y - 3), C['brow'])
            if blink:
                F.line((ex, hc_y - 1), (ex + 1, hc_y - 1), P['skin'][3])
            else:
                F.px((ex, hc_y - 1), C['white']); F.px((ex + 1, hc_y - 1), C['eye']); F.px((ex + 1, hc_y), C['eye'])
                if turn: F.px((ex + (1 if turn > 0 else 0), hc_y - 1), C['eye'])
            F.line((ex, hc_y + 1), (ex + 1, hc_y + 1), P['skin'][2])
        F.line((hc_x + t, hc_y), (hc_x + t, hc_y + 3), P['skin'][2]); F.px((hc_x + 1 + t, hc_y + 4), P['skin'][2])
        F.px((hc_x - 1 + t, hc_y + 4), P['skin'][2])
        for y in range(hc_y + 4, hc_y + 11):
            for x in range(hc_x - 7, hc_x + 8):
                if (x + y) % 2 == 0 and F.arr[y, x, 3] and tuple(F.arr[y, x]) in (P['skin'][1], P['skin'][2], P['skin'][0]) \
                   and not (abs(x - hc_x - t) <= 2 and y == hc_y + 6):
                    F.px((x, y), C['stub2'] if tuple(F.arr[y, x]) == P['skin'][2] else C['stub'])
        if mouth: F.rect(hc_x - 1 + t, hc_y + 6, hc_x + 1 + t, hc_y + 7, C['mouthin'])
        else: F.line((hc_x - 2 + t, hc_y + 6), (hc_x + 2 + t, hc_y + 6), C['mouth'])
    else:
        F.line((hc_x - 4, hc_y + 6), (hc_x + 4, hc_y + 6), P['hair'][2])

    # arms
    def arm(shx, el, hd, sd):
        sp = (shx, sy + 4 - s)
        e = add(sp, (el[0] * K, el[1] * K)); h = add(sp, (hd[0] * K, hd[1] * K))
        def sl(d): cap(d, sp, e, 8); cap(d, e, h, 8)
        F.part(sl, 'coat', sw=2)
        hv = (h[0] - e[0], h[1] - e[1]); n = math.hypot(*hv) or 1
        c0 = add(h, (-hv[0] / n * 4, -hv[1] / n * 4))
        F.part(lambda d: cap(d, c0, h, 9), 'coat', sw=1)
        hp = add(h, (hv[0] / n * 4, hv[1] / n * 4))
        x, y = R(hp)
        F.part(lambda d: d.ellipse([x - 3, y - 3, x + 3, y + 4], fill=255), 'skin', sw=1)
        return hp
    L = lhand or ((-2, 11), (-2, 21))
    Rr = rhand or ((2, 11), (2, 21))
    arm(cx - 15, *L, -1)
    hp = arm(cx + 15, *Rr, 1)
    if badge:
        x, y = R(arm(cx - 15, *L, -1)) if False else R(add((cx - 15, sy + 4 - s), (L[1][0] * K, L[1][1] * K)))
        F.part(lambda d: d.rectangle([x - 4, y - 8, x + 4, y + 1], fill=255), 'leather', sw=1)
        F.rect(x - 2, y - 7, x + 2, y - 3, C['gold']); F.rect(x - 1, y - 2, x + 1, y - 2, C['gold'])
        F.px((x, y - 1), C['gold'])
        if badge == 2: F.px((x - 1, y - 6), C['goldH']); F.px((x + 4, y - 9), C['goldH']); F.px((x + 5, y - 10), C['goldH'])
        F.part(lambda d: d.ellipse([x - 3, y, x + 3, y + 5], fill=255), 'skin', sw=1)
    return F.img()

# ======================================================================== animations
anims = []
anims.append(('idle_right', [side(), side(b=1), side(b=1), side(blink=1)], 4, True))
walk = []
for i in range(8):
    ph = 2 * math.pi * i / 8
    walk.append(side(lean=3,
                     ft=26 * math.sin(ph), fk=6 + 36 * max(0, math.cos(ph)),
                     bt=26 * math.sin(ph + math.pi), bk=6 + 36 * max(0, math.cos(ph + math.pi)),
                     fu=-18 * math.sin(ph), ff=-18 * math.sin(ph) + 16,
                     bu=18 * math.sin(ph), bf=18 * math.sin(ph) + 16))
anims.append(('walk_right', walk, 10, True))
anims.append(('idle_down', [front(), front(bob=-1), front(bob=-1), front(blink=1)], 4, True))
def fwalk(back=False):
    out = []
    for i in range(8):
        ph = 2 * math.pi * i / 8; sv = math.sin(ph)
        dep = 2 * math.cos(ph) * (-1 if back else 1)
        lsw = max(0, -sv); rsw = max(0, sv)
        out.append(front(ll=max(0, sv), rl=max(0, -sv), ld=dep, rd=-dep, back=back,
                         bob=-1 if i % 4 == 2 else 0,
                         lhand=((-2, 11 - lsw), (-1 + lsw, 21 - 3 * lsw)),
                         rhand=((2, 11 - rsw), (1 - rsw, 21 - 3 * rsw))))
    return out
anims.append(('walk_down', fwalk(), 10, True))
anims.append(('idle_up', [front(back=True), front(back=True, bob=-1)], 2, True))
anims.append(('walk_up', fwalk(True), 10, True))
anims.append(('talk_right', [side(mouth=1, fu=14, ff=70), side(fu=18, ff=86), side(mouth=1, fu=10, ff=58), side()], 6, True))
anims.append(('talk_down', [front(mouth=1, rhand=((5, 9), (1, 6))), front(rhand=((5, 9), (0, 4))),
                            front(mouth=1, rhand=((5, 9), (2, 8))), front()], 6, True))
pk = [side(),
      side(lean=15, ft=30, fk=48, bt=-4, bk=36, fu=12, ff=24, bu=-2, bf=10, coat=32),
      side(lean=36, ft=74, fk=120, bt=14, bk=112, fu=-6, ff=4, bu=0, bf=8, hdy=1, coat=26),
      side(lean=36, ft=74, fk=120, bt=14, bk=112, fu=-6, ff=4, bu=0, bf=8, hdy=1, hold='box', coat=26),
      side(lean=15, ft=30, fk=48, bt=-4, bk=36, fu=14, ff=60, bu=-2, bf=10, hold='box', coat=32),
      side(fu=10, ff=105, hold='box')]
anims.append(('pickup_right', pk, 8, False))
anims.append(('use_right', [side(), side(fu=40, ff=62), side(fu=72, ff=84), side(fu=74, ff=96)], 8, False))
nbk = [side(), side(fu=14, ff=150, hdy=1), side(fu=16, ff=108, hold='notebook', hdy=1),
       side(fu=16, ff=108, hold='notebook', hdy=1, bu=28, bf=112, pen=True),
       side(fu=16, ff=108, hold='notebook', hdy=1, bu=30, bf=118, pen=True), side(fu=14, ff=150, hdy=1)]
anims.append(('notebook_right', nbk, 6, False))
anims.append(('look_around', [front(), front(turn=-1), front(), front(turn=1)], 2, True))
anims.append(('shrug', [front(), front(shrug=0.5, lhand=((-5, 10), (-9, 14)), rhand=((5, 10), (9, 14))),
                        front(shrug=1, lhand=((-6, 9), (-12, 6)), rhand=((6, 9), (12, 6)), hdy=1),
                        front(shrug=0.5, lhand=((-5, 10), (-9, 14)), rhand=((5, 10), (9, 14)))], 6, False))
anims.append(('show_badge', [front(), front(lhand=((-1, 11), (4, 14)), badge=1),
                             front(lhand=((-1, 11), (5, 6)), badge=1),
                             front(lhand=((-1, 11), (5, 6)), badge=2)], 6, False))
for name, fr, fps, loop in list(anims):
    if name.endswith('_right'):
        anims.append((name.replace('_right', '_left'), [f.transpose(Image.FLIP_LEFT_RIGHT) for f in fr], fps, loop))

# ======================================================================== export
COLS = 8
sheet = Image.new('RGBA', (FW * COLS, FH * len(anims)), (0, 0, 0, 0))
meta = dict(frameWidth=FW, frameHeight=FH, columns=COLS, pivot=[48, GROUND],
            note='pivot = feet ground-contact point in frame pixels', animations={})
for r, (name, fr, fps, loop) in enumerate(anims):
    for c, f in enumerate(fr): sheet.paste(f, (c * FW, r * FH))
    meta['animations'][name] = dict(row=r, frames=len(fr), fps=fps, loop=loop,
                                    rects=[[c * FW, r * FH, FW, FH] for c in range(len(fr))])
sheet.save('detective_pixel.png')
sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save('detective_pixel@3x.png')
json.dump(meta, open('detective_pixel.json', 'w'), indent=1)

S = 3; LW = 170
ref = Image.new('RGBA', (LW + FW * COLS * S, FH * S * len(anims)), (226, 220, 206, 255))
d = ImageDraw.Draw(ref)
try:
    fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
except Exception: fb = fs = ImageFont.load_default()
for r, (name, fr, fps, loop) in enumerate(anims):
    y = r * FH * S
    if r % 2: d.rectangle([0, y, ref.width, y + FH * S], fill=(214, 207, 192, 255))
    d.text((12, y + FH * S // 2 - 18), name, fill=(36, 32, 36), font=fb)
    d.text((12, y + FH * S // 2 + 4), f'{len(fr)}f · {fps}fps', fill=(110, 100, 96), font=fs)
    for c, f in enumerate(fr):
        ref.alpha_composite(f.resize((FW * S, FH * S), Image.NEAREST), (LW + c * FW * S, y))
ref.convert('RGB').save('detective_pixel_reference.png')

show = ['idle_down', 'walk_right', 'walk_down', 'walk_up', 'talk_right', 'pickup_right',
        'notebook_right', 'shrug', 'show_badge', 'look_around']
A = {n: (fr, fps) for n, fr, fps, _ in anims}
S2 = 3; frames = []
for t in range(60):
    canvas = Image.new('RGBA', (FW * S2 * 5, FH * S2 * 2), (198, 190, 174, 255))
    for k, n in enumerate(show):
        fr, fps = A[n]
        canvas.alpha_composite(fr[int(t * fps / 10) % len(fr)].resize((FW * S2, FH * S2), Image.NEAREST),
                               ((k % 5) * FW * S2, (k // 5) * FH * S2))
    frames.append(canvas.convert('RGB'))
frames[0].save('detective_pixel_preview.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)
print(sheet.size, len(anims))
