// r3: SDF scene renderer for Nightshift art.
// Perspective or orthographic camera, many lights with soft shadows, emissive and
// textured materials, one-bounce wet reflections, ambient occlusion, and a separate
// low-resolution volumetric (fog + light shafts) pass. Uniform grid acceleration.
//
// Usage: r3 scene.bin out_prefix
// The surface and volumetric passes run on the GPU through OpenCL (r3_gpu.h, r3.cl) when one is available,
// else on the CPU with OpenMP. Set R3_DEVICE=cpu or R3_DEVICE=gpu to force one (gpu fails rather than falling back).
// Writes out_prefix.surf (float32 RGBA linear, W*H*4), out_prefix.depth (float32 W*H),
// out_prefix.vol (float32 4 per pixel: inscatter rgb + transmittance at W/vs x H/vs).
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdint.h>

typedef struct { float x, y, z; } v3;
static inline v3 V(float x, float y, float z) { v3 r = {x, y, z}; return r; }
static inline v3 add(v3 a, v3 b) { return V(a.x + b.x, a.y + b.y, a.z + b.z); }
static inline v3 sub(v3 a, v3 b) { return V(a.x - b.x, a.y - b.y, a.z - b.z); }
static inline v3 mul(v3 a, float s) { return V(a.x * s, a.y * s, a.z * s); }
static inline v3 vmul(v3 a, v3 b) { return V(a.x * b.x, a.y * b.y, a.z * b.z); }
static inline float dot(v3 a, v3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static inline float len(v3 a) { return sqrtf(dot(a, a)); }
static inline v3 nrm(v3 a) { float l = len(a); return l > 0 ? mul(a, 1.0f / l) : a; }
static inline v3 cross(v3 a, v3 b) { return V(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x); }
static inline float clampf(float x, float a, float b) { return x < a ? a : (x > b ? b : x); }
static inline float mixf(float a, float b, float t) { return a + (b - a) * t; }
static inline v3 vmix(v3 a, v3 b, float t) { return add(mul(a, 1 - t), mul(b, t)); }
static inline float smooth(float e0, float e1, float x) { float t = clampf((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); }

// ---------------------------------------------------------------- data
#define PF 48
typedef struct {
    int type, mat, op; float k;
    v3 a, b; float ra, rb;
    float R[9]; v3 c, r;
    int clip; v3 cn; float co;
    float shell; int clip2; v3 cn2; float co2; int inmat;
    v3 bc; float br;
} Prim;
#define DF 28
typedef struct { int from, to, np; v3 n[6]; float o[6]; float feather; } Decal;
#define MF 32
typedef struct {
    v3 col; float spec, shin, namp, nscale, bump, bscale, wrap, aniso;
    v3 emis; float refl, rough; int tex, texmode, texmap; float texscale, texemis, ripple;
} Mat;
#define LF 20
typedef struct { int type; v3 p, d, col; float range, cosi, coso; int shadow; float vol; int volshadow; float soft; } Light;
typedef struct { int w, h; float *px; } Tex;

static Prim *P; static int NP;
static Decal *D; static int ND;
static Mat *M; static int NM;
static Light *L; static int NL;
static Tex *T; static int NT;

// camera / globals
static int W, H, ORTHO, VS;
static v3 CP, CF, CR, CU; static float FOV, OH;
static v3 SKY, BOUNCE, FOGC; static float FOGD, FOGH0, FOGHF, FOGMAX, AOS;
static int REFL, SHADOWS;

// ---------------------------------------------------------------- noise
static inline float hash3(int x, int y, int z) {
    uint32_t h = (uint32_t)x * 374761393u + (uint32_t)y * 668265263u + (uint32_t)z * 2147483647u;
    h = (h ^ (h >> 13)) * 1274126177u; h ^= h >> 16;
    return (h & 0xffffff) / 16777215.0f;
}
static float vnoise(v3 p) {
    float fx = floorf(p.x), fy = floorf(p.y), fz = floorf(p.z);
    int ix = (int)fx, iy = (int)fy, iz = (int)fz;
    float ux = p.x - fx, uy = p.y - fy, uz = p.z - fz;
    ux = ux * ux * (3 - 2 * ux); uy = uy * uy * (3 - 2 * uy); uz = uz * uz * (3 - 2 * uz);
    float a = mixf(hash3(ix, iy, iz), hash3(ix + 1, iy, iz), ux);
    float b = mixf(hash3(ix, iy + 1, iz), hash3(ix + 1, iy + 1, iz), ux);
    float c = mixf(hash3(ix, iy, iz + 1), hash3(ix + 1, iy, iz + 1), ux);
    float d = mixf(hash3(ix, iy + 1, iz + 1), hash3(ix + 1, iy + 1, iz + 1), ux);
    return mixf(mixf(a, b, uy), mixf(c, d, uy), uz);
}
static float fbm(v3 p) {
    float s = 0, a = 0.5f;
    for (int i = 0; i < 4; i++) { s += a * vnoise(p); p = mul(p, 2.03f); a *= 0.5f; }
    return s / 0.9375f;
}

// ---------------------------------------------------------------- SDFs
static inline v3 loc(const Prim *p, v3 q) {
    v3 d = sub(q, p->c); const float *R = p->R;
    return V(R[0] * d.x + R[1] * d.y + R[2] * d.z, R[3] * d.x + R[4] * d.y + R[5] * d.z,
             R[6] * d.x + R[7] * d.y + R[8] * d.z);
}
static float sdRoundCone(v3 p, v3 a, v3 b, float r1, float r2) {
    v3 ba = sub(b, a); float l2 = dot(ba, ba);
    if (l2 < 1e-10f) return len(sub(p, a)) - r1;
    float rr = r1 - r2, a2 = l2 - rr * rr, il2 = 1.0f / l2;
    v3 pa = sub(p, a); float y = dot(pa, ba), z = y - l2;
    v3 xv = sub(mul(pa, l2), mul(ba, y)); float x2 = dot(xv, xv);
    float y2 = y * y * l2, z2 = z * z * l2;
    float k = copysignf(1.0f, rr) * rr * rr * x2;
    if (copysignf(1.0f, z) * a2 * z2 > k) return sqrtf(x2 + z2) * il2 - r2;
    if (copysignf(1.0f, y) * a2 * y2 < k) return sqrtf(x2 + y2) * il2 - r1;
    return (sqrtf(x2 * a2 * il2) + y * rr) * il2 - r1;
}
static int g_inner;
#pragma omp threadprivate(g_inner)
static inline float primDist(const Prim *p, v3 q) {
    float d;
    switch (p->type) {
    case 0: d = sdRoundCone(q, p->a, p->b, p->ra, p->rb); break;
    case 1: {
        v3 l = loc(p, q);
        v3 a = V(l.x / p->r.x, l.y / p->r.y, l.z / p->r.z);
        v3 b = V(a.x / p->r.x, a.y / p->r.y, a.z / p->r.z);
        float k0 = len(a), k1 = len(b);
        d = k1 > 1e-9f ? k0 * (k0 - 1.0f) / k1 : -fminf(p->r.x, fminf(p->r.y, p->r.z));
        break; }
    case 2: {
        v3 l = loc(p, q);
        v3 qq = V(fabsf(l.x) - p->r.x + p->ra, fabsf(l.y) - p->r.y + p->ra, fabsf(l.z) - p->r.z + p->ra);
        v3 m = V(fmaxf(qq.x, 0), fmaxf(qq.y, 0), fmaxf(qq.z, 0));
        d = len(m) + fminf(fmaxf(qq.x, fmaxf(qq.y, qq.z)), 0.0f) - p->ra;
        break; }
    case 4: {
        v3 l = loc(p, q);
        float t = clampf((l.y + p->r.z) / (2 * p->r.z), 0, 1);
        float rx = mixf(p->a.x, p->r.x, t), rz = mixf(p->a.y, p->r.y, t);
        float ax = l.x / rx, az = l.z / rz;
        float k0 = sqrtf(ax * ax + az * az), k1 = sqrtf(ax * ax / (rx * rx) + az * az / (rz * rz));
        float d2 = k1 > 1e-9f ? k0 * (k0 - 1.0f) / k1 : -fminf(rx, rz);
        d = fmaxf(d2, fabsf(l.y) - p->r.z);
        break; }
    default: d = len(sub(q, p->a)) - p->ra;
    }
    g_inner = d < 0;
    if (p->shell > 0) d = fabsf(d) - p->shell;
    if (p->clip) d = fmaxf(d, p->co - dot(q, p->cn));
    if (p->clip2) d = fmaxf(d, p->co2 - dot(q, p->cn2));
    return d;
}

// ---------------------------------------------------------------- grid
static v3 GMIN, GMAX; static float GCS; static int GX, GY, GZ;
static int *GSTART, *GCOUNT, *GLIST;

static void build_grid(float cs) {
    GMIN = V(1e9, 1e9, 1e9); GMAX = V(-1e9, -1e9, -1e9);
    for (int i = 0; i < NP; i++) {
        Prim *p = &P[i];
        if (p->op) continue;
        GMIN = V(fminf(GMIN.x, p->bc.x - p->br), fminf(GMIN.y, p->bc.y - p->br), fminf(GMIN.z, p->bc.z - p->br));
        GMAX = V(fmaxf(GMAX.x, p->bc.x + p->br), fmaxf(GMAX.y, p->bc.y + p->br), fmaxf(GMAX.z, p->bc.z + p->br));
    }
    GMIN = sub(GMIN, V(0.05f, 0.05f, 0.05f)); GMAX = add(GMAX, V(0.05f, 0.05f, 0.05f));
    GCS = cs;
    GX = (int)ceilf((GMAX.x - GMIN.x) / cs); GY = (int)ceilf((GMAX.y - GMIN.y) / cs); GZ = (int)ceilf((GMAX.z - GMIN.z) / cs);
    if (GX < 1) GX = 1; if (GY < 1) GY = 1; if (GZ < 1) GZ = 1;
    int nc = GX * GY * GZ;
    GSTART = calloc(nc, sizeof(int)); GCOUNT = calloc(nc, sizeof(int));
    float margin = cs;
    // each prim's cell range (its bounding sphere grown by margin)
    int *rng = malloc(sizeof(int) * 6 * (NP + 1));
    for (int i = 0; i < NP; i++) {
        Prim *p = &P[i]; int *g = rng + 6 * i;
        float r = p->br + margin;
        g[0] = (int)floorf((p->bc.x - r - GMIN.x) / cs); g[1] = (int)floorf((p->bc.x + r - GMIN.x) / cs);
        g[2] = (int)floorf((p->bc.y - r - GMIN.y) / cs); g[3] = (int)floorf((p->bc.y + r - GMIN.y) / cs);
        g[4] = (int)floorf((p->bc.z - r - GMIN.z) / cs); g[5] = (int)floorf((p->bc.z + r - GMIN.z) / cs);
        if (g[0] < 0) g[0] = 0; if (g[2] < 0) g[2] = 0; if (g[4] < 0) g[4] = 0;
        if (g[1] >= GX) g[1] = GX - 1; if (g[3] >= GY) g[3] = GY - 1; if (g[5] >= GZ) g[5] = GZ - 1;
    }
    for (int pass = 0; pass < 2; pass++) {
        if (pass == 1) {
            int tot = 0;
            for (int c = 0; c < nc; c++) { GSTART[c] = tot; tot += GCOUNT[c]; GCOUNT[c] = 0; }
            GLIST = malloc(sizeof(int) * (tot + 1));
        }
        // threads own z slices, so no two touch the same cell, and each cell still lists its prims in order
        int z;
        #pragma omp parallel for schedule(dynamic, 1)
        for (z = 0; z < GZ; z++)
            for (int i = 0; i < NP; i++) {
                Prim *p = &P[i]; const int *g = rng + 6 * i;
                if (z < g[4] || z > g[5]) continue;
                float r = p->br + margin;
                float czmin = GMIN.z + z * cs;
                float dz = fmaxf(fmaxf(czmin - p->bc.z, 0), p->bc.z - (czmin + cs));
                for (int y = g[2]; y <= g[3]; y++) {
                    float cymin = GMIN.y + y * cs;
                    float dy = fmaxf(fmaxf(cymin - p->bc.y, 0), p->bc.y - (cymin + cs));
                    float q = r * r - dy * dy - dz * dz;
                    if (q < 0) continue;
                    // only the cells near the sphere's chord through this row (one spare cell each side)
                    float sx = sqrtf(q);
                    int x0 = (int)floorf((p->bc.x - sx - GMIN.x) / cs) - 1, x1 = (int)floorf((p->bc.x + sx - GMIN.x) / cs) + 1;
                    if (x0 < g[0]) x0 = g[0]; if (x1 > g[1]) x1 = g[1];
                    for (int x = x0; x <= x1; x++) {
                        // sphere vs cell box test
                        v3 cmin = V(GMIN.x + x * cs, cymin, czmin);
                        float dx = fmaxf(fmaxf(cmin.x - p->bc.x, 0), p->bc.x - (cmin.x + cs));
                        if (dx * dx + dy * dy + dz * dz > r * r) continue;
                        int c = (z * GY + y) * GX + x;
                        if (pass == 1) GLIST[GSTART[c] + GCOUNT[c]] = i;
                        GCOUNT[c]++;
                    }
                }
            }
    }
    free(rng);
}

static int g_prim;
#pragma omp threadprivate(g_prim)

static float map(v3 q, int *mat) {
    // outside the grid: distance to its box
    float ox = fmaxf(GMIN.x - q.x, q.x - GMAX.x), oy = fmaxf(GMIN.y - q.y, q.y - GMAX.y), oz = fmaxf(GMIN.z - q.z, q.z - GMAX.z);
    float out = fmaxf(ox, fmaxf(oy, oz));
    if (out > 0) { if (mat) *mat = -1; return out + 0.02f; }
    int x = (int)((q.x - GMIN.x) / GCS), y = (int)((q.y - GMIN.y) / GCS), z = (int)((q.z - GMIN.z) / GCS);
    if (x >= GX) x = GX - 1; if (y >= GY) y = GY - 1; if (z >= GZ) z = GZ - 1;
    int c = (z * GY + y) * GX + x;
    float d = 1e9f; int m = -1, pi = -1;
    const int *lst = GLIST + GSTART[c]; int n = GCOUNT[c];
    for (int j = 0; j < n; j++) {
        const Prim *p = &P[lst[j]];
        float lb = len(sub(q, p->bc)) - p->br;
        if (p->op == 0) {
            if (lb > fminf(d, GCS) + p->k) continue;
            float di = primDist(p, q);
            int mm = (g_inner && p->inmat >= 0) ? p->inmat : p->mat;
            if (p->k > 0) {
                float h = fmaxf(p->k - fabsf(d - di), 0.0f) / p->k;
                if (di < d) { m = mm; pi = lst[j]; }
                d = fminf(d, di) - h * h * p->k * 0.25f;
            } else if (di < d) { d = di; m = mm; pi = lst[j]; }
        } else {
            if (lb > -d + p->k) continue;
            float di = primDist(p, q);
            if (p->k > 0) {
                float h = fmaxf(p->k - fabsf(d + di), 0.0f) / p->k;
                d = fmaxf(d, -di) + h * h * p->k * 0.25f;
            } else d = fmaxf(d, -di);
        }
    }
    if (mat) { *mat = m; g_prim = pi; }
    return fminf(d, GCS);
}

static v3 normal(v3 p, float e) {
    v3 k1 = V(1, -1, -1), k2 = V(-1, -1, 1), k3 = V(-1, 1, -1), k4 = V(1, 1, 1);
    v3 n = add(add(mul(k1, map(add(p, mul(k1, e)), 0)), mul(k2, map(add(p, mul(k2, e)), 0))),
               add(mul(k3, map(add(p, mul(k3, e)), 0)), mul(k4, map(add(p, mul(k4, e)), 0))));
    return nrm(n);
}

static int applyDecals(v3 p, int m) {
    for (int i = 0; i < ND; i++) {
        Decal *dc = &D[i];
        if (dc->from != m) continue;
        int in = 1;
        float fz = dc->feather > 0 ? dc->feather * (fbm(mul(p, 90.0f)) - 0.5f) * 2.0f : 0.0f;
        for (int j = 0; j < dc->np; j++) if (dot(p, dc->n[j]) >= dc->o[j] + fz) { in = 0; break; }
        if (in) m = dc->to;
    }
    return m;
}

// ---------------------------------------------------------------- textures
static inline void tex_sample(const Tex *t, float u, float v, float out[4]) {
    u = u - floorf(u); v = v - floorf(v);
    float x = u * t->w - 0.5f, y = v * t->h - 0.5f;
    int x0 = (int)floorf(x), y0 = (int)floorf(y); float fx = x - x0, fy = y - y0;
    for (int k = 0; k < 4; k++) out[k] = 0;
    for (int j = 0; j < 2; j++) for (int i = 0; i < 2; i++) {
        int xx = ((x0 + i) % t->w + t->w) % t->w, yy = ((y0 + j) % t->h + t->h) % t->h;
        float w = (i ? fx : 1 - fx) * (j ? fy : 1 - fy);
        const float *px = t->px + (yy * t->w + xx) * 4;
        for (int k = 0; k < 4; k++) out[k] += px[k] * w;
    }
}

static void mat_tex(const Mat *mt, int prim, v3 p, v3 n, float out[4]) {
    const Tex *t = &T[mt->tex];
    if (mt->texmap == 0 && prim >= 0) {
        const Prim *pr = &P[prim];
        v3 l = loc(pr, p);
        float u = l.x / (2 * pr->r.x) + 0.5f, v = 0.5f - l.y / (2 * pr->r.y);
        if (u < 0 || u > 1 || v < 0 || v > 1) { out[0] = out[1] = out[2] = out[3] = 0; return; }
        tex_sample(t, u, v, out);
    } else {
        float s = 1.0f / mt->texscale;
        float ax = fabsf(n.x), ay = fabsf(n.y), az = fabsf(n.z);
        float a[4], b[4], c[4];
        tex_sample(t, p.z * s, -p.y * s, a);
        tex_sample(t, p.x * s, p.z * s, b);
        tex_sample(t, p.x * s, -p.y * s, c);
        float wsum = ax * ax * ax * ax + ay * ay * ay * ay + az * az * az * az + 1e-6f;
        for (int k = 0; k < 4; k++) out[k] = (a[k] * ax * ax * ax * ax + b[k] * ay * ay * ay * ay + c[k] * az * az * az * az) / wsum;
    }
}

// ---------------------------------------------------------------- lighting
static float softshadow(v3 ro, v3 rd, float maxt, float k) {
    float res = 1.0f, t = 0.01f;
    for (int i = 0; i < 64 && t < maxt; i++) {
        float h = map(add(ro, mul(rd, t)), 0);
        res = fminf(res, k * h / t);
        if (res < 0.02f) return 0.0f;
        t += clampf(h, 0.01f, 0.5f);
    }
    return clampf(res, 0, 1);
}
static float ambocc(v3 p, v3 n) {
    float occ = 0, w = 1;
    for (int i = 1; i <= 5; i++) {
        float h = AOS * (0.02f * i * i + 0.01f);
        float d = map(add(p, mul(n, h)), 0);
        occ += (h - d) * w; w *= 0.7f;
    }
    return clampf(1.0f - 2.2f * occ / AOS, 0, 1);
}
static inline float atten(const Light *l, float d) {
    if (l->type == 2) return 1.0f;
    float a = 1.0f / (1.0f + d * d);
    float f = 1.0f - smooth(l->range * 0.6f, l->range, d);
    return a * f;
}
static inline float conef(const Light *l, v3 dirToPoint) {
    if (l->type != 1) return 1.0f;
    float c = dot(dirToPoint, l->d);
    return smooth(l->coso, l->cosi, c);
}

static int trace(v3 ro, v3 rd, float tmax, int steps, float *tout, v3 *pout, int *mout) {
    float t = 0.0f; int m;
    for (int i = 0; i < steps; i++) {
        v3 p = add(ro, mul(rd, t));
        float d = map(p, &m);
        float eps = 0.0004f * (1.0f + t * 0.6f);
        if (d < eps) { *tout = t; *pout = p; *mout = m; return 1; }
        t += d * 0.9f;
        if (t > tmax) break;
    }
    *tout = tmax; return 0;
}

static v3 shade(v3 p, v3 rd, int m, int prim, float t, int depth);

static v3 fogged(v3 col, float t) {
    float T = expf(-FOGD * 0.6f * t);
    return vmix(FOGC, col, T);
}

static v3 shade(v3 p, v3 rd, int m, int prim, float t, int depth) {
    float ne = 0.0007f * (1.0f + t * 0.4f);
    v3 n = normal(p, ne);
    m = applyDecals(p, m);
    if (m < 0) m = 0;
    const Mat *mt = &M[m];
    if (mt->bump > 0) {
        float e = 0.35f;
        v3 q = mul(p, mt->bscale);
        float b0 = fbm(q);
        v3 g = V(fbm(add(q, V(e, 0, 0))) - b0, fbm(add(q, V(0, e, 0))) - b0, fbm(add(q, V(0, 0, e))) - b0);
        n = nrm(sub(n, mul(g, mt->bump)));
    }
    v3 alb = mt->col;
    if (mt->namp > 0) {
        float nz = mt->aniso > 0 ? vnoise(V(p.x * mt->nscale, p.y * mt->nscale * 0.25f, p.z * mt->nscale)) : fbm(mul(p, mt->nscale));
        alb = mul(alb, 1.0f + mt->namp * (nz - 0.5f) * 2.0f);
    }
    v3 emis = mt->emis;
    if (mt->tex >= 0 && mt->texmode > 0) {
        float tx[4]; mat_tex(mt, prim, p, n, tx);
        v3 tc = V(tx[0], tx[1], tx[2]);
        if (mt->texmode == 1 || mt->texmode == 3) alb = vmix(alb, vmul(tc, mt->texmode == 3 ? V(1, 1, 1) : V(1, 1, 1)), tx[3]);
        if (mt->texmode == 1 && mt->namp > 0) alb = alb;
        if (mt->texmode == 2 || mt->texmode == 3) emis = add(emis, mul(tc, tx[3] * mt->texemis));
        if (mt->texmode == 4) alb = vmul(alb, tc);  // multiply
    }
    float ao = ambocc(p, n);
    v3 col = vmul(alb, add(mul(SKY, (0.5f + 0.5f * n.y) * ao), mul(BOUNCE, (0.5f - 0.5f * n.y) * ao)));
    v3 po = add(p, mul(n, 0.004f * (1 + t * 0.3f)));
    for (int i = 0; i < NL; i++) {
        const Light *l = &L[i];
        v3 ld; float dist;
        if (l->type == 2) { ld = mul(l->d, -1); dist = 1e3f; }
        else { v3 dv = sub(l->p, p); dist = len(dv); ld = mul(dv, 1.0f / dist); if (dist > l->range) continue; }
        float a = atten(l, dist) * conef(l, mul(ld, -1));
        if (a < 1e-4f) continue;
        float nl = dot(n, ld);
        float w = mt->wrap;
        float dif = clampf((nl + w) / (1 + w), 0, 1);
        if (dif <= 0 && mt->spec <= 0) continue;
        float sh = 1.0f;
        if (l->shadow && SHADOWS && nl > -w) sh = softshadow(po, ld, fminf(dist, 40.0f) - fmaxf(0.35f, 0.04f * dist), l->soft);
        if (sh <= 0) continue;
        v3 lc = mul(l->col, a * sh);
        col = add(col, vmul(alb, mul(lc, dif)));
        if (mt->spec > 0 && nl > 0) {
            v3 h = nrm(sub(ld, rd));
            float s = powf(clampf(dot(n, h), 0, 1), mt->shin) * mt->spec;
            col = add(col, mul(lc, s));
        }
    }
    col = add(col, emis);
    if (REFL && mt->refl > 0 && depth == 0) {
        v3 nr = n;
        if (mt->ripple > 0) {
            // streaky: varies fast across x, slowly in depth -> reflections stretch vertically on screen
            float s1 = vnoise(V(p.x * 16.0f, 0.5f, p.z * 0.9f)) - 0.5f;
            float s2 = vnoise(V(p.x * 3.0f + 7, 1.5f, p.z * 2.0f)) - 0.5f;
            float s3 = vnoise(V(p.x * 40.0f, 2.5f, p.z * 40.0f)) - 0.5f;
            nr = nrm(add(n, V(s2 * mt->ripple * 0.25f + s3 * 0.03f, 0, s1 * mt->ripple)));
        }
        v3 rr = sub(rd, mul(nr, 2 * dot(rd, nr)));
        float cosv = clampf(-dot(rd, n), 0, 1);
        float fr = mt->refl * (0.04f + 0.96f * powf(1 - cosv, 5)) + mt->refl * 0.25f;
        fr = clampf(fr, 0, 1);
        float tr; v3 pr; int mr;
        v3 rc;
        if (trace(po, rr, 40.0f, 140, &tr, &pr, &mr)) rc = fogged(shade(pr, rr, mr, g_prim, t + tr, 1), tr);
        else rc = FOGC;
        // wet surfaces darken the diffuse
        col = add(mul(col, 1.0f - fr * 0.85f), mul(rc, fr));
    }
    return col;
}

// ---------------------------------------------------------------- camera rays
static void camray(float sx, float sy, v3 *ro, v3 *rd) {
    float nx = (sx / W) * 2 - 1, ny = 1 - (sy / H) * 2;
    float aspect = (float)W / H;
    if (ORTHO) {
        *ro = add(CP, add(mul(CR, nx * OH * 0.5f * aspect), mul(CU, ny * OH * 0.5f)));
        *rd = CF;
    } else {
        float th = tanf(FOV * 0.5f);
        *ro = CP;
        *rd = nrm(add(CF, add(mul(CR, nx * th * aspect), mul(CU, ny * th))));
    }
}

static inline float fogdens(v3 p) {
    float h = fmaxf(p.y - FOGH0, 0);
    return FOGD * expf(-h * FOGHF);
}

static const float BAYER4[16] = {0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5};

// ---------------------------------------------------------------- probe mode
// r3 scene.bin out_prefix probes.bin : for each probe point write, per light, the light's
// attenuation x cone x soft shadow at that point, then the fog seen from the camera up to the point
// (inscatter rgb, transmittance). Used to relight the sprite characters in the game.
static void run_probes(const char *path, const char *outp, int vsteps) {
    FILE *f = fopen(path, "rb"); int n = 0;
    if (!f || fread(&n, 4, 1, f) != 1) return;
    float *pts = malloc(sizeof(float) * 3 * n);
    if (fread(pts, 4, 3 * n, f) != (size_t)(3 * n)) return;
    fclose(f);
    int stride = NL + 4;
    float *out = calloc((size_t)n * stride, 4);
    int i;   // declared outside the loop for MSVC's OpenMP 2.0
    #pragma omp parallel for schedule(dynamic, 4)
    for (i = 0; i < n; i++) {
        v3 p = V(pts[i * 3], pts[i * 3 + 1], pts[i * 3 + 2]);
        for (int k = 0; k < NL; k++) {
            const Light *l = &L[k];
            v3 ld; float dist;
            if (l->type == 2) { ld = mul(l->d, -1); dist = 1e3f; }
            else { v3 dv = sub(l->p, p); dist = len(dv); ld = mul(dv, 1.0f / dist); if (dist > l->range) continue; }
            float a = atten(l, dist) * conef(l, mul(ld, -1));
            if (a < 1e-5f) continue;
            float sh = 1.0f;
            if (l->shadow && SHADOWS) sh = softshadow(p, ld, fminf(dist, 40.0f) - fmaxf(0.35f, 0.04f * dist), l->soft);
            out[(size_t)i * stride + k] = a * sh;
        }
        // fog between the camera and the point
        v3 ro = CP, dv = sub(p, CP); float tend = len(dv); v3 rd = mul(dv, 1.0f / tend);
        v3 acc = V(0, 0, 0); float Tr = 1.0f;
        if (FOGD > 0) {
            float dt = tend / vsteps;
            for (int s = 0; s < vsteps; s++) {
                v3 q = add(ro, mul(rd, (s + 0.5f) * dt));
                float dens = fogdens(q);
                if (dens <= 1e-6f) continue;
                v3 li = FOGC;
                for (int k = 0; k < NL; k++) {
                    const Light *l = &L[k];
                    if (l->vol <= 0) continue;
                    v3 ld; float dist;
                    if (l->type == 2) { ld = mul(l->d, -1); dist = 1e3f; }
                    else { v3 d2 = sub(l->p, q); dist = len(d2); if (dist > l->range) continue; ld = mul(d2, 1.0f / dist); }
                    float a = atten(l, dist) * conef(l, mul(ld, -1));
                    if (a < 1e-4f) continue;
                    float cth = dot(rd, ld);
                    float g = 0.35f, ph = (1 - g * g) / powf(1 + g * g - 2 * g * cth, 1.5f) * 0.25f;
                    float sh = 1.0f;
                    if (l->volshadow && SHADOWS) sh = softshadow(q, ld, fminf(dist, 30.0f) - 0.35f, 30.0f);
                    li = add(li, mul(l->col, a * ph * sh * l->vol));
                }
                float ext = expf(-dens * dt);
                acc = add(acc, mul(li, Tr * (1 - ext)));
                Tr *= ext;
            }
        }
        float *o = out + (size_t)i * stride + NL;
        o[0] = acc.x; o[1] = acc.y; o[2] = acc.z; o[3] = Tr;
    }
    f = fopen(outp, "wb"); fwrite(out, 4, (size_t)n * stride, f); fclose(f);
}

#include "r3_gpu.h"

// ---------------------------------------------------------------- main
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb");
    float hdr[64]; if (fread(hdr, 4, 64, f) != 64) return 1;
    W = hdr[0]; H = hdr[1]; ORTHO = hdr[2];
    CP = V(hdr[3], hdr[4], hdr[5]); v3 tgt = V(hdr[6], hdr[7], hdr[8]);
    FOV = hdr[9]; OH = hdr[10];
    SKY = V(hdr[11], hdr[12], hdr[13]); BOUNCE = V(hdr[14], hdr[15], hdr[16]);
    FOGC = V(hdr[17], hdr[18], hdr[19]); FOGD = hdr[20]; FOGH0 = hdr[21]; FOGHF = hdr[22]; FOGMAX = hdr[23];
    NP = hdr[24]; ND = hdr[25]; NM = hdr[26]; NL = hdr[27]; NT = hdr[28];
    REFL = hdr[29]; SHADOWS = hdr[30]; VS = hdr[31]; float gcs = hdr[32]; AOS = hdr[33];
    v3 upv = V(hdr[34], hdr[35], hdr[36]);
    int VSTEPS = hdr[37] > 0 ? (int)hdr[37] : 40;
    if (AOS <= 0) AOS = 1;
    CF = nrm(sub(tgt, CP)); CR = nrm(cross(CF, upv)); CU = cross(CR, CF);

    P = calloc(NP + 1, sizeof(Prim)); D = calloc(ND + 1, sizeof(Decal)); M = calloc(NM + 1, sizeof(Mat));
    L = calloc(NL + 1, sizeof(Light)); T = calloc(NT + 1, sizeof(Tex));
    float buf[64];
    for (int i = 0; i < NP; i++) {
        if (fread(buf, 4, PF, f) != PF) return 2;
        Prim *p = &P[i];
        p->type = buf[0]; p->mat = buf[1]; p->op = buf[2]; p->k = buf[3];
        p->a = V(buf[4], buf[5], buf[6]); p->b = V(buf[7], buf[8], buf[9]); p->ra = buf[10]; p->rb = buf[11];
        memcpy(p->R, buf + 12, 36); p->c = V(buf[21], buf[22], buf[23]); p->r = V(buf[24], buf[25], buf[26]);
        p->clip = buf[27]; p->cn = V(buf[28], buf[29], buf[30]); p->co = buf[31];
        p->bc = V(buf[32], buf[33], buf[34]); p->br = buf[35];
        p->shell = buf[36]; p->clip2 = buf[37]; p->cn2 = V(buf[38], buf[39], buf[40]); p->co2 = buf[41];
        p->inmat = (int)buf[42] - 1;
    }
    for (int i = 0; i < ND; i++) {
        if (fread(buf, 4, DF, f) != DF) return 3;
        Decal *d = &D[i];
        d->from = buf[0]; d->to = buf[1]; d->np = buf[2]; d->feather = buf[27];
        for (int j = 0; j < d->np; j++) { d->n[j] = V(buf[3 + j * 4], buf[4 + j * 4], buf[5 + j * 4]); d->o[j] = buf[6 + j * 4]; }
    }
    for (int i = 0; i < NM; i++) {
        if (fread(buf, 4, MF, f) != MF) return 4;
        Mat *m = &M[i];
        m->col = V(buf[0], buf[1], buf[2]); m->spec = buf[3]; m->shin = buf[4]; m->namp = buf[5]; m->nscale = buf[6];
        m->bump = buf[7]; m->bscale = buf[8]; m->wrap = buf[9]; m->aniso = buf[10];
        m->emis = V(buf[11], buf[12], buf[13]); m->refl = buf[14]; m->rough = buf[15];
        m->tex = (int)buf[16]; m->texmode = buf[17]; m->texmap = buf[18]; m->texscale = buf[19]; m->texemis = buf[20];
        m->ripple = buf[21];
    }
    for (int i = 0; i < NL; i++) {
        if (fread(buf, 4, LF, f) != LF) return 5;
        Light *l = &L[i];
        l->type = buf[0]; l->p = V(buf[1], buf[2], buf[3]); l->d = nrm(V(buf[4], buf[5], buf[6]));
        l->col = V(buf[7], buf[8], buf[9]); l->range = buf[10]; l->cosi = buf[11]; l->coso = buf[12];
        l->shadow = buf[13]; l->vol = buf[14]; l->volshadow = buf[15]; l->soft = buf[16] > 0 ? buf[16] : 12;
    }
    for (int i = 0; i < NT; i++) {
        int wh[2]; if (fread(wh, 4, 2, f) != 2) return 6;
        T[i].w = wh[0]; T[i].h = wh[1];
        T[i].px = malloc(sizeof(float) * 4 * wh[0] * wh[1]);
        unsigned char *b = malloc(4 * wh[0] * wh[1]);
        if (fread(b, 1, 4 * wh[0] * wh[1], f) != (size_t)(4 * wh[0] * wh[1])) return 7;
        for (int k = 0; k < wh[0] * wh[1]; k++) {
            for (int c = 0; c < 3; c++) T[i].px[k * 4 + c] = powf(b[k * 4 + c] / 255.0f, 2.2f);
            T[i].px[k * 4 + 3] = b[k * 4 + 3] / 255.0f;
        }
        free(b);
    }
    fclose(f);
    build_grid(gcs > 0 ? gcs : 0.6f);
    if (argc > 3) {
        char pn[1024]; snprintf(pn, sizeof pn, "%s.probe", argv[2]);
        run_probes(argv[3], pn, VSTEPS);
        return 0;
    }

    int n = W * H;
    float *S = calloc((size_t)n * 4, 4), *DEP = malloc((size_t)n * 4);
    int volw = VS > 0 ? W / VS : 0, volh = VS > 0 ? H / VS : 0;
    float *VO = (VS > 0 && FOGD > 0) ? calloc((size_t)volw * volh * 4, 4) : NULL;
    const char *dev = getenv("R3_DEVICE");
    int gpu_done = 0;
    if (!dev || strcmp(dev, "cpu") != 0) {
        gpu_done = gpu_render(argv[0], S, DEP, VO, VSTEPS) == 0;
        if (!gpu_done && dev && strcmp(dev, "gpu") == 0) return 8;
        if (!gpu_done) fprintf(stderr, "r3: rendering on the CPU instead\n");
    }
    char nm[1024];
    int y;
    if (gpu_done) goto write_out;

    // ---- surface pass
    #pragma omp parallel for schedule(dynamic, 1)
    for (y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            v3 ro, rd; camray(x + 0.5f, y + 0.5f, &ro, &rd);
            float t; v3 p; int m;
            int i = y * W + x;
            if (trace(ro, rd, FOGMAX, 400, &t, &p, &m)) {
                v3 c = shade(p, rd, m, g_prim, t, 0);
                S[i * 4] = c.x; S[i * 4 + 1] = c.y; S[i * 4 + 2] = c.z; S[i * 4 + 3] = 1;
                DEP[i] = t;
            } else {
                S[i * 4] = FOGC.x; S[i * 4 + 1] = FOGC.y; S[i * 4 + 2] = FOGC.z; S[i * 4 + 3] = 0;
                DEP[i] = FOGMAX;
            }
        }

    // ---- volumetric pass (low res)
    if (VO) {
        int vw = volw, vh = volh;
        #pragma omp parallel for schedule(dynamic, 1)
        for (y = 0; y < vh; y++)
            for (int x = 0; x < vw; x++) {
                // depth = minimum of the hi-res block, so fog doesn't bleed past near edges
                float tend = FOGMAX;
                for (int j = 0; j < VS; j++) for (int i = 0; i < VS; i++) {
                    float dd = DEP[(y * VS + j) * W + x * VS + i]; if (dd < tend) tend = dd;
                }
                v3 ro, rd; camray((x + 0.5f) * VS, (y + 0.5f) * VS, &ro, &rd);
                float dt = tend / VSTEPS;
                float jit = (BAYER4[(y & 3) * 4 + (x & 3)] + 0.5f) / 16.0f;
                v3 acc = V(0, 0, 0); float Tr = 1.0f;
                for (int s = 0; s < VSTEPS; s++) {
                    float tt = (s + jit) * dt;
                    v3 q = add(ro, mul(rd, tt));
                    float dens = fogdens(q);
                    if (dens <= 1e-6f) continue;
                    v3 li = FOGC;
                    for (int k = 0; k < NL; k++) {
                        const Light *l = &L[k];
                        if (l->vol <= 0) continue;
                        v3 ld; float dist;
                        if (l->type == 2) { ld = mul(l->d, -1); dist = 1e3f; }
                        else { v3 dv = sub(l->p, q); dist = len(dv); if (dist > l->range) continue; ld = mul(dv, 1.0f / dist); }
                        float a = atten(l, dist) * conef(l, mul(ld, -1));
                        if (a < 1e-4f) continue;
                        float cth = dot(rd, ld);
                        float g = 0.35f, ph = (1 - g * g) / powf(1 + g * g - 2 * g * cth, 1.5f) * 0.25f;
                        float sh = 1.0f;
                        if (l->volshadow && SHADOWS) sh = softshadow(q, ld, fminf(dist, 30.0f) - 0.35f, 30.0f);
                        li = add(li, mul(l->col, a * ph * sh * l->vol));
                    }
                    float ext = expf(-dens * dt);
                    acc = add(acc, mul(li, Tr * (1 - ext)));
                    Tr *= ext;
                }
                int i = y * vw + x;
                VO[i * 4] = acc.x; VO[i * 4 + 1] = acc.y; VO[i * 4 + 2] = acc.z; VO[i * 4 + 3] = Tr;
            }
    }

write_out:
    snprintf(nm, sizeof nm, "%s.surf", argv[2]); f = fopen(nm, "wb"); fwrite(S, 4, (size_t)n * 4, f); fclose(f);
    snprintf(nm, sizeof nm, "%s.depth", argv[2]); f = fopen(nm, "wb"); fwrite(DEP, 4, n, f); fclose(f);
    if (VO) { snprintf(nm, sizeof nm, "%s.vol", argv[2]); f = fopen(nm, "wb"); fwrite(VO, 4, (size_t)volw * volh * 4, f); fclose(f); }
    return 0;
}
