"""Cars for the Case 4 sets: a generic modern sedan or SUV built from rounded boxes, in its own frame.

Car-local axes (as in mulholland_overlook.py): x toward the passenger side, y up, z toward the tail; the nose is at -z.
car(S, ...) returns a function pt(x, y, z) -> world point, for placing hotspots and people around it."""
import math
import numpy as np
from scene3d import Frame, Ry, Rx, Rz, nrm


def mats(S, name, paint, lights=True):
    """Materials for one car, prefixed with its name."""
    S.mat(f'{name}_paint', paint, spec=1.3, shin=90, refl=0.35)
    S.mat(f'{name}_glass', (10, 12, 16), spec=1.5, shin=120, refl=0.55)
    S.mat(f'{name}_trim', (20, 20, 22), spec=0.4, shin=30)
    S.mat(f'{name}_tire', (16, 16, 18))
    S.mat(f'{name}_rim', (150, 150, 156), spec=1.2, shin=60, refl=0.3)
    S.mat(f'{name}_interior', (30, 30, 34), namp=0.2, nscale=30)
    S.mat(f'{name}_seat', (40, 40, 46), namp=0.25, nscale=24, spec=0.2)
    if lights:
        S.mat(f'{name}_head', (240, 240, 230), emis=(255, 250, 235), emis_mult=3)
        S.mat(f'{name}_tail', (130, 10, 10), emis=(255, 30, 30), emis_mult=1.6)
    else:
        S.mat(f'{name}_head', (200, 204, 210), spec=1.6, shin=100, refl=0.4)
        S.mat(f'{name}_tail', (110, 16, 16), spec=1.2, shin=80, refl=0.3)
    S.mat(f'{name}_hole', (6, 6, 8))


def car(S, name, origin, yaw, paint, L=4.9, W=1.86, H=1.45, kind='sedan', lights=True, tag=None,
        rear_door_open=0.0, door_side=-1, broken='', dent=False, interior=False):
    """Build a car with its floor centre at `origin`, nose pointing along -z turned by `yaw` degrees.
    kind: 'sedan' | 'suv' | 'hatch'. rear_door_open: degrees a rear door stands open (shows the back seat),
    door_side: -1 the driver's side, 1 the passenger's. broken: 'r' or 'l' leaves that headlight a black hole. interior: model seats (for open doors)."""
    mats(S, name, paint, lights)
    F = Frame(origin, Ry(yaw))
    pt = lambda x, y, z: tuple(F.to((x, y, z)))
    hw, hl = W / 2, L / 2
    m = lambda k: f'{name}_{k}'

    def box(c, half, mat, rnd=0.0, rot=None, op=0, k=0):
        return S.box(F, c, half, rnd, mat, rot=rot, op=op, k=k)

    ctx = S.tag(tag) if tag else None
    if ctx:
        S._tag = tag
    belt = 0.92 if kind == 'suv' else 0.82                      # top of the doors
    sill = 0.42 if kind == 'suv' else 0.3
    # lower body: a long rounded slab, a bit narrower at the nose and tail
    box((0, (sill + belt) / 2, 0), (hw, (belt - sill) / 2 + 0.02, hl - 0.05), m('paint'), rnd=0.12)
    box((0, belt - 0.06, -hl + 0.55), (hw - 0.05, 0.08, 0.55), m('paint'), rnd=0.08, rot=Rx(5))      # hood
    # the greenhouse: one glass block cut by the windshield and back-glass planes, a painted roof and pillars over it
    if kind == 'suv':
        c0, c1, rf, fr, bk = -hl + 1.75, hl - 0.25, H, 0.6, 0.12
    elif kind == 'hatch':
        c0, c1, rf, fr, bk = -hl + 1.75, hl - 0.55, H, 0.75, 0.35
    else:
        c0, c1, rf, fr, bk = -hl + 1.95, hl - 1.25, H, 0.85, 0.75
    cz = (c0 + c1) / 2
    gh = rf - belt
    zf0, zb1 = c0 - fr, c1 + bk                                   # where the glass meets the body, front and back

    def plane(n, p0):
        n = nrm(n)
        return F.plane(n, float(n @ np.asarray(p0, float)))
    pf = plane((0, -(c0 - zf0), gh), (0, belt, zf0))
    pb = plane((0, -(zb1 - c1), -gh), (0, belt, zb1))
    for mat_, inset, top in ((m('glass'), 0.1, rf - 0.02), (m('paint'), 0.08, rf)):
        if mat_ == m('paint'):                                    # the roof: the same block, only its top skin
            S._add(2, mat_, 0, 0, R=F.M.T, c=F.to((0, rf - 0.02, (zf0 + zb1) / 2)),
                   r=np.array([hw - inset, 0.035, (zb1 - zf0) / 2]), ra=0.03, clip=(pf[0], pf[1] + 0.03),
                   clip2=(pb[0], pb[1] + 0.03))
        else:
            S._add(2, mat_, 0, 0, R=F.M.T, c=F.to((0, belt + gh / 2 - 0.01, (zf0 + zb1) / 2)),
                   r=np.array([hw - inset, gh / 2, (zb1 - zf0) / 2]), ra=0.04, clip=pf, clip2=pb,
                   shell=0.012 if interior else 0)

    def slab(p0, p1, half_w, half_t, mat_):
        """A thin bar from car-local p0 to p1."""
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        z = nrm(p1 - p0); x = nrm(np.cross((0, 1, 0), z)) if abs(z[1]) < 0.99 else np.array([1.0, 0, 0])
        y = np.cross(z, x)
        S.box(F, (p0 + p1) / 2, (half_w, half_t, np.linalg.norm(p1 - p0) / 2), 0.01, mat_,
              rot=np.column_stack([x, y, z]))
    for sx in (-1, 1):
        ex = sx * (hw - 0.1)
        slab((ex, belt, zf0), (ex, rf - 0.02, c0), 0.04, 0.04, m('paint'))                    # A pillars
        slab((ex, belt, zb1), (ex, rf - 0.02, c1), 0.05, 0.05, m('paint'))                    # C pillars
        slab((ex, belt, cz + 0.05), (ex, rf - 0.02, cz + 0.02), 0.035, 0.035, m('trim'))       # B pillars
    if interior:                                                  # a hollow cabin: glaze the cut planes
        for (pa, pb_) in (((0, belt, zf0), (0, rf - 0.02, c0)), ((0, belt, zb1), (0, rf - 0.02, c1))):
            slab(pa, pb_, hw - 0.12, 0.01, m('glass'))
    if kind == 'sedan':
        box((0, belt + 0.01, (zb1 + hl) / 2), (hw - 0.06, 0.03, (hl - zb1) / 2), m('paint'), rnd=0.03)   # trunk lid
    # lights, grille, bumpers
    for sx in (-1, 1):
        side = 'l' if sx < 0 else 'r'
        hx = sx * (hw - 0.32)
        if broken == side:
            box((hx, belt - 0.14, -hl + 0.04), (0.24, 0.06, 0.06), m('hole'), rnd=0.01)
            for k in range(4):                                                  # jagged edges left in the housing
                a = k * math.pi / 2 + 0.4
                box((hx + 0.17 * math.cos(a), belt - 0.14 + 0.045 * math.sin(a), -hl + 0.02),
                    (0.04, 0.012, 0.012), m('head'), rot=Rz(math.degrees(a) + 30))
        else:
            box((hx, belt - 0.14, -hl + 0.04), (0.24, 0.05, 0.05), m('head'), rnd=0.02, rot=Ry(-sx * 6))
        box((sx * (hw - 0.22), belt - 0.12, hl - 0.02), (0.2, 0.05, 0.04), m('tail'), rnd=0.01)
    box((0, belt - 0.22, -hl + 0.02), (0.38, 0.1, 0.03), m('trim'), rnd=0.02)                          # grille
    box((0, sill + 0.06, -hl + 0.02), (hw - 0.08, 0.08, 0.06), m('trim'), rnd=0.03)                   # bumpers
    box((0, sill + 0.06, hl - 0.02), (hw - 0.08, 0.08, 0.06), m('trim'), rnd=0.03)
    if dent:
        S.ell(F, (hw - 0.55, belt + 0.02, -hl + 0.6), (0.3, 0.06, 0.25), m('paint'), op=1, k=0.06)
    if rear_door_open:
        # carve a rear door out, show the back seat, and hang the door open on its front edge
        ds = door_side
        box((ds * hw, (sill + belt) / 2 + 0.05, cz + 0.55), (0.25, (belt - sill) / 2 + 0.02, 0.48), m('paint'), op=1)
        box((ds * (hw - 0.1), belt + gh / 2, cz + 0.55), (0.2, gh / 2 + 0.02, 0.48), m('paint'), op=1)
        box((0, sill + 0.05, cz + 0.4), (hw - 0.15, 0.04, 0.9), m('interior'))
        box((0, sill + 0.2, cz + 0.75), (hw - 0.2, 0.08, 0.28), m('seat'), rnd=0.04)                  # back seat
        box((0, belt + 0.12, cz + 1.02), (hw - 0.2, 0.36, 0.07), m('seat'), rnd=0.05, rot=Rx(-12))
        box((0, belt + 0.18, cz - 0.05), (hw - 0.15, gh / 2 + 0.1, 0.03), m('trim'))                  # cage
        hinge = np.array(pt(ds * hw, 0, cz + 0.07))
        D = Frame(hinge, Ry(yaw) @ Ry(ds * rear_door_open))
        S.box(D, (0, (sill + belt) / 2 + 0.05, 0.48), (0.05, (belt - sill) / 2, 0.47), 0.03, m('paint'))
        S.box(D, (-ds * 0.05, (sill + belt) / 2 + 0.05, 0.48), (0.01, (belt - sill) / 2 - 0.03, 0.43), 0.01,
              m('interior'))
        S.box(D, (0, belt + gh / 2, 0.46), (0.015, gh / 2 - 0.02, 0.42), 0.01, m('glass'))
    # wheels
    wb = L * 0.3
    for sx in (-1, 1):
        for wz in (-wb, wb):
            wf = Frame(pt(sx * (hw - 0.12), 0.33, wz), Ry(yaw) @ Rz(90))
            S.tcyl(wf, (0, 0, 0), (0.33, 0.33), (0.33, 0.33), 0.11, m('tire'))
            S.tcyl(wf, (0, -0.11 * sx, 0), (0.2, 0.2), (0.2, 0.2), 0.012, m('rim'))
    if ctx:
        S._tag = None
    return pt
