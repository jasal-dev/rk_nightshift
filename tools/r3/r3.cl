// r3.cl: the GPU (OpenCL) port of r3.c's surface and volumetric passes.
// Keep it in step with r3.c: every function here mirrors the one of the same name there.
// r3.exe loads this file from its own folder and builds it at run time.

typedef struct {
    int type, mat, op; float k;
    float a[3], b[3]; float ra, rb;
    float R[9]; float c[3], r[3];
    int clip; float cn[3]; float co;
    float shell; int clip2; float cn2[3]; float co2; int inmat;
    float bc[3]; float br;
} Prim;
typedef struct { int from, to, np; float n[6][3]; float o[6]; float feather; } Decal;
typedef struct {
    float col[3]; float spec, shin, namp, nscale, bump, bscale, wrap, aniso;
    float emis[3]; float refl, rough; int tex, texmode, texmap; float texscale, texemis, ripple;
} Mat;
typedef struct { int type; float p[3], d[3], col[3]; float range, cosi, coso; int shadow; float vol; int volshadow; float soft; } Light;
typedef struct { int w, h, off; } Tex;   // off: first texel in TX (float4 units)
typedef struct {
    int W, H, ORTHO, VS, VSTEPS, REFL, SHADOWS, NL, ND, GX, GY, GZ, pad0, pad1;
    float CP[3], CF[3], CR[3], CU[3]; float FOV, OH;
    float SKY[3], BOUNCE[3], FOGC[3]; float FOGD, FOGH0, FOGHF, FOGMAX, AOS;
    float GMIN[3], GMAX[3]; float GCS;
} Glob;

typedef struct {
    __constant Glob *g;
    __global const Prim *P; __global const Decal *D; __global const Mat *M; __global const Light *L;
    __global const Tex *T; __global const float *TX;
    __global const int *GSTART, *GCOUNT, *GLIST;
    int inner, prim;
} Ctx;

#define F3(a) ((float3)((a)[0], (a)[1], (a)[2]))
#define V(x, y, z) ((float3)((x), (y), (z)))

inline float3 nrm(float3 a) { float l = sqrt(dot(a, a)); return l > 0 ? a * (1.0f / l) : a; }
inline float len3(float3 a) { return sqrt(dot(a, a)); }
inline float clampf(float x, float a, float b) { return x < a ? a : (x > b ? b : x); }
inline float mixf(float a, float b, float t) { return a + (b - a) * t; }
inline float3 vmix(float3 a, float3 b, float t) { return a * (1 - t) + b * t; }
inline float smooth(float e0, float e1, float x) { float t = clampf((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); }

// ---------------------------------------------------------------- noise
inline float hash3(int x, int y, int z) {
    uint h = (uint)x * 374761393u + (uint)y * 668265263u + (uint)z * 2147483647u;
    h = (h ^ (h >> 13)) * 1274126177u; h ^= h >> 16;
    return (h & 0xffffff) / 16777215.0f;
}
float vnoise(float3 p) {
    float fx = floor(p.x), fy = floor(p.y), fz = floor(p.z);
    int ix = (int)fx, iy = (int)fy, iz = (int)fz;
    float ux = p.x - fx, uy = p.y - fy, uz = p.z - fz;
    ux = ux * ux * (3 - 2 * ux); uy = uy * uy * (3 - 2 * uy); uz = uz * uz * (3 - 2 * uz);
    float a = mixf(hash3(ix, iy, iz), hash3(ix + 1, iy, iz), ux);
    float b = mixf(hash3(ix, iy + 1, iz), hash3(ix + 1, iy + 1, iz), ux);
    float c = mixf(hash3(ix, iy, iz + 1), hash3(ix + 1, iy, iz + 1), ux);
    float d = mixf(hash3(ix, iy + 1, iz + 1), hash3(ix + 1, iy + 1, iz + 1), ux);
    return mixf(mixf(a, b, uy), mixf(c, d, uy), uz);
}
float fbm(float3 p) {
    float s = 0, a = 0.5f;
    for (int i = 0; i < 4; i++) { s += a * vnoise(p); p = p * 2.03f; a *= 0.5f; }
    return s / 0.9375f;
}

// ---------------------------------------------------------------- SDFs
inline float3 loc(__global const Prim *p, float3 q) {
    float3 d = q - F3(p->c);
    return V(p->R[0] * d.x + p->R[1] * d.y + p->R[2] * d.z, p->R[3] * d.x + p->R[4] * d.y + p->R[5] * d.z,
             p->R[6] * d.x + p->R[7] * d.y + p->R[8] * d.z);
}
float sdRoundCone(float3 p, float3 a, float3 b, float r1, float r2) {
    float3 ba = b - a; float l2 = dot(ba, ba);
    if (l2 < 1e-10f) return len3(p - a) - r1;
    float rr = r1 - r2, a2 = l2 - rr * rr, il2 = 1.0f / l2;
    float3 pa = p - a; float y = dot(pa, ba), z = y - l2;
    float3 xv = pa * l2 - ba * y; float x2 = dot(xv, xv);
    float y2 = y * y * l2, z2 = z * z * l2;
    float k = copysign(1.0f, rr) * rr * rr * x2;
    if (copysign(1.0f, z) * a2 * z2 > k) return sqrt(x2 + z2) * il2 - r2;
    if (copysign(1.0f, y) * a2 * y2 < k) return sqrt(x2 + y2) * il2 - r1;
    return (sqrt(x2 * a2 * il2) + y * rr) * il2 - r1;
}
float primDist(Ctx *C, __global const Prim *p, float3 q) {
    float d;
    switch (p->type) {
    case 0: d = sdRoundCone(q, F3(p->a), F3(p->b), p->ra, p->rb); break;
    case 1: {
        float3 l = loc(p, q), r = F3(p->r);
        float3 a = l / r, b = a / r;
        float k0 = len3(a), k1 = len3(b);
        d = k1 > 1e-9f ? k0 * (k0 - 1.0f) / k1 : -fmin(r.x, fmin(r.y, r.z));
        break; }
    case 2: {
        float3 l = loc(p, q);
        float3 qq = V(fabs(l.x) - p->r[0] + p->ra, fabs(l.y) - p->r[1] + p->ra, fabs(l.z) - p->r[2] + p->ra);
        float3 m = fmax(qq, (float3)(0.0f));
        d = len3(m) + fmin(fmax(qq.x, fmax(qq.y, qq.z)), 0.0f) - p->ra;
        break; }
    case 4: {
        float3 l = loc(p, q);
        float t = clampf((l.y + p->r[2]) / (2 * p->r[2]), 0, 1);
        float rx = mixf(p->a[0], p->r[0], t), rz = mixf(p->a[1], p->r[1], t);
        float ax = l.x / rx, az = l.z / rz;
        float k0 = sqrt(ax * ax + az * az), k1 = sqrt(ax * ax / (rx * rx) + az * az / (rz * rz));
        float d2 = k1 > 1e-9f ? k0 * (k0 - 1.0f) / k1 : -fmin(rx, rz);
        d = fmax(d2, fabs(l.y) - p->r[2]);
        break; }
    default: d = len3(q - F3(p->a)) - p->ra;
    }
    C->inner = d < 0;
    if (p->shell > 0) d = fabs(d) - p->shell;
    if (p->clip) d = fmax(d, p->co - dot(q, F3(p->cn)));
    if (p->clip2) d = fmax(d, p->co2 - dot(q, F3(p->cn2)));
    return d;
}

// ---------------------------------------------------------------- grid
// wantmat: 1 to fill *mat and C->prim (like passing a mat pointer to map() in r3.c)
float map(Ctx *C, float3 q, int *mat, int wantmat) {
    __constant Glob *g = C->g;
    float3 gmin = F3(g->GMIN), gmax = F3(g->GMAX);
    float ox = fmax(gmin.x - q.x, q.x - gmax.x), oy = fmax(gmin.y - q.y, q.y - gmax.y), oz = fmax(gmin.z - q.z, q.z - gmax.z);
    float out = fmax(ox, fmax(oy, oz));
    if (out > 0) { if (wantmat) *mat = -1; return out + 0.02f; }
    float gcs = g->GCS;
    int x = (int)((q.x - gmin.x) / gcs), y = (int)((q.y - gmin.y) / gcs), z = (int)((q.z - gmin.z) / gcs);
    if (x >= g->GX) x = g->GX - 1; if (y >= g->GY) y = g->GY - 1; if (z >= g->GZ) z = g->GZ - 1;
    int c = (z * g->GY + y) * g->GX + x;
    float d = 1e9f; int m = -1, pi = -1;
    __global const int *lst = C->GLIST + C->GSTART[c]; int n = C->GCOUNT[c];
    for (int j = 0; j < n; j++) {
        int idx = lst[j];
        __global const Prim *p = C->P + idx;
        float lb = len3(q - F3(p->bc)) - p->br;
        if (p->op == 0) {
            if (lb > fmin(d, gcs) + p->k) continue;
            float di = primDist(C, p, q);
            int mm = (C->inner && p->inmat >= 0) ? p->inmat : p->mat;
            if (p->k > 0) {
                float h = fmax(p->k - fabs(d - di), 0.0f) / p->k;
                if (di < d) { m = mm; pi = idx; }
                d = fmin(d, di) - h * h * p->k * 0.25f;
            } else if (di < d) { d = di; m = mm; pi = idx; }
        } else {
            if (lb > -d + p->k) continue;
            float di = primDist(C, p, q);
            if (p->k > 0) {
                float h = fmax(p->k - fabs(d + di), 0.0f) / p->k;
                d = fmax(d, -di) + h * h * p->k * 0.25f;
            } else d = fmax(d, -di);
        }
    }
    if (wantmat) { *mat = m; C->prim = pi; }
    return fmin(d, gcs);
}
inline float mapd(Ctx *C, float3 q) { int m; return map(C, q, &m, 0); }

float3 normal(Ctx *C, float3 p, float e) {
    float3 k1 = V(1, -1, -1), k2 = V(-1, -1, 1), k3 = V(-1, 1, -1), k4 = V(1, 1, 1);
    float3 n = k1 * mapd(C, p + k1 * e) + k2 * mapd(C, p + k2 * e) + k3 * mapd(C, p + k3 * e) + k4 * mapd(C, p + k4 * e);
    return nrm(n);
}

int applyDecals(Ctx *C, float3 p, int m) {
    int nd = C->g->ND;
    for (int i = 0; i < nd; i++) {
        __global const Decal *dc = C->D + i;
        if (dc->from != m) continue;
        int in = 1;
        float fz = dc->feather > 0 ? dc->feather * (fbm(p * 90.0f) - 0.5f) * 2.0f : 0.0f;
        for (int j = 0; j < dc->np; j++) if (dot(p, F3(dc->n[j])) >= dc->o[j] + fz) { in = 0; break; }
        if (in) m = dc->to;
    }
    return m;
}

// ---------------------------------------------------------------- textures
float4 tex_sample(Ctx *C, __global const Tex *t, float u, float v) {
    u = u - floor(u); v = v - floor(v);
    float x = u * t->w - 0.5f, y = v * t->h - 0.5f;
    int x0 = (int)floor(x), y0 = (int)floor(y); float fx = x - x0, fy = y - y0;
    float4 out = (float4)(0.0f);
    for (int j = 0; j < 2; j++) for (int i = 0; i < 2; i++) {
        int xx = ((x0 + i) % t->w + t->w) % t->w, yy = ((y0 + j) % t->h + t->h) % t->h;
        float w = (i ? fx : 1 - fx) * (j ? fy : 1 - fy);
        out += vload4(t->off + yy * t->w + xx, C->TX) * w;
    }
    return out;
}

float4 mat_tex(Ctx *C, __global const Mat *mt, int prim, float3 p, float3 n) {
    __global const Tex *t = C->T + mt->tex;
    if (mt->texmap == 0 && prim >= 0) {
        __global const Prim *pr = C->P + prim;
        float3 l = loc(pr, p);
        float u = l.x / (2 * pr->r[0]) + 0.5f, v = 0.5f - l.y / (2 * pr->r[1]);
        if (u < 0 || u > 1 || v < 0 || v > 1) return (float4)(0.0f);
        return tex_sample(C, t, u, v);
    }
    float s = 1.0f / mt->texscale;
    float ax = fabs(n.x), ay = fabs(n.y), az = fabs(n.z);
    float4 a = tex_sample(C, t, p.z * s, -p.y * s);
    float4 b = tex_sample(C, t, p.x * s, p.z * s);
    float4 c = tex_sample(C, t, p.x * s, -p.y * s);
    float wa = ax * ax * ax * ax, wb = ay * ay * ay * ay, wc = az * az * az * az;
    float wsum = wa + wb + wc + 1e-6f;
    return (a * wa + b * wb + c * wc) / wsum;
}

// ---------------------------------------------------------------- lighting
float softshadow(Ctx *C, float3 ro, float3 rd, float maxt, float k) {
    float res = 1.0f, t = 0.01f;
    for (int i = 0; i < 64 && t < maxt; i++) {
        float h = mapd(C, ro + rd * t);
        res = fmin(res, k * h / t);
        if (res < 0.02f) return 0.0f;
        t += clampf(h, 0.01f, 0.5f);
    }
    return clampf(res, 0, 1);
}
float ambocc(Ctx *C, float3 p, float3 n) {
    float aos = C->g->AOS;
    float occ = 0, w = 1;
    for (int i = 1; i <= 5; i++) {
        float h = aos * (0.02f * i * i + 0.01f);
        float d = mapd(C, p + n * h);
        occ += (h - d) * w; w *= 0.7f;
    }
    return clampf(1.0f - 2.2f * occ / aos, 0, 1);
}
inline float atten(__global const Light *l, float d) {
    if (l->type == 2) return 1.0f;
    float a = 1.0f / (1.0f + d * d);
    float f = 1.0f - smooth(l->range * 0.6f, l->range, d);
    return a * f;
}
inline float conef(__global const Light *l, float3 dirToPoint) {
    if (l->type != 1) return 1.0f;
    float c = dot(dirToPoint, F3(l->d));
    return smooth(l->coso, l->cosi, c);
}

int trace(Ctx *C, float3 ro, float3 rd, float tmax, int steps, float *tout, float3 *pout, int *mout) {
    float t = 0.0f; int m;
    for (int i = 0; i < steps; i++) {
        float3 p = ro + rd * t;
        float d = map(C, p, &m, 1);
        float eps = 0.0004f * (1.0f + t * 0.6f);
        if (d < eps) { *tout = t; *pout = p; *mout = m; return 1; }
        t += d * 0.9f;
        if (t > tmax) break;
    }
    *tout = tmax; return 0;
}

float3 fogged(Ctx *C, float3 col, float t) {
    float T = exp(-C->g->FOGD * 0.6f * t);
    return vmix(F3(C->g->FOGC), col, T);
}

// shade() in r3.c without the reflection bounce (OpenCL has no recursion); returns the lit colour,
// the shading normal and the material, so shade0() can add the bounce
float3 shade_base(Ctx *C, float3 p, float3 rd, int m, int prim, float t, float3 *nout, int *mout) {
    __constant Glob *g = C->g;
    float ne = 0.0007f * (1.0f + t * 0.4f);
    float3 n = normal(C, p, ne);
    m = applyDecals(C, p, m);
    if (m < 0) m = 0;
    __global const Mat *mt = C->M + m;
    if (mt->bump > 0) {
        float e = 0.35f;
        float3 q = p * mt->bscale;
        float b0 = fbm(q);
        float3 gr = V(fbm(q + V(e, 0, 0)) - b0, fbm(q + V(0, e, 0)) - b0, fbm(q + V(0, 0, e)) - b0);
        n = nrm(n - gr * mt->bump);
    }
    float3 alb = F3(mt->col);
    if (mt->namp > 0) {
        float nz = mt->aniso > 0 ? vnoise(V(p.x * mt->nscale, p.y * mt->nscale * 0.25f, p.z * mt->nscale)) : fbm(p * mt->nscale);
        alb = alb * (1.0f + mt->namp * (nz - 0.5f) * 2.0f);
    }
    float3 emis = F3(mt->emis);
    if (mt->tex >= 0 && mt->texmode > 0) {
        float4 tx = mat_tex(C, mt, prim, p, n);
        float3 tc = tx.xyz;
        if (mt->texmode == 1 || mt->texmode == 3) alb = vmix(alb, tc, tx.w);
        if (mt->texmode == 2 || mt->texmode == 3) emis = emis + tc * (tx.w * mt->texemis);
        if (mt->texmode == 4) alb = alb * tc;
    }
    float ao = ambocc(C, p, n);
    float3 col = alb * (F3(g->SKY) * ((0.5f + 0.5f * n.y) * ao) + F3(g->BOUNCE) * ((0.5f - 0.5f * n.y) * ao));
    float3 po = p + n * (0.004f * (1 + t * 0.3f));
    for (int i = 0; i < g->NL; i++) {
        __global const Light *l = C->L + i;
        float3 ld; float dist;
        if (l->type == 2) { ld = -F3(l->d); dist = 1e3f; }
        else { float3 dv = F3(l->p) - p; dist = len3(dv); ld = dv * (1.0f / dist); if (dist > l->range) continue; }
        float a = atten(l, dist) * conef(l, -ld);
        if (a < 1e-4f) continue;
        float nl = dot(n, ld);
        float w = mt->wrap;
        float dif = clampf((nl + w) / (1 + w), 0, 1);
        if (dif <= 0 && mt->spec <= 0) continue;
        float sh = 1.0f;
        if (l->shadow && g->SHADOWS && nl > -w) sh = softshadow(C, po, ld, fmin(dist, 40.0f) - fmax(0.35f, 0.04f * dist), l->soft);
        if (sh <= 0) continue;
        float3 lc = F3(l->col) * (a * sh);
        col = col + alb * (lc * dif);
        if (mt->spec > 0 && nl > 0) {
            float3 h = nrm(ld - rd);
            float s = pow(clampf(dot(n, h), 0, 1), mt->shin) * mt->spec;
            col = col + lc * s;
        }
    }
    *nout = n; *mout = m;
    return col + emis;
}

float3 shade0(Ctx *C, float3 p, float3 rd, int m, int prim, float t) {
    __constant Glob *g = C->g;
    float3 n;
    float3 col = shade_base(C, p, rd, m, prim, t, &n, &m);
    __global const Mat *mt = C->M + m;
    if (g->REFL && mt->refl > 0) {
        float3 po = p + n * (0.004f * (1 + t * 0.3f));
        float3 nr = n;
        if (mt->ripple > 0) {
            float s1 = vnoise(V(p.x * 16.0f, 0.5f, p.z * 0.9f)) - 0.5f;
            float s2 = vnoise(V(p.x * 3.0f + 7, 1.5f, p.z * 2.0f)) - 0.5f;
            float s3 = vnoise(V(p.x * 40.0f, 2.5f, p.z * 40.0f)) - 0.5f;
            nr = nrm(n + V(s2 * mt->ripple * 0.25f + s3 * 0.03f, 0, s1 * mt->ripple));
        }
        float3 rr = rd - nr * (2 * dot(rd, nr));
        float cosv = clampf(-dot(rd, n), 0, 1);
        float fr = mt->refl * (0.04f + 0.96f * pow(1 - cosv, 5)) + mt->refl * 0.25f;
        fr = clampf(fr, 0, 1);
        float tr; float3 pr; int mr;
        float3 rc;
        if (trace(C, po, rr, 40.0f, 140, &tr, &pr, &mr)) {
            float3 n2; int m2;
            rc = fogged(C, shade_base(C, pr, rr, mr, C->prim, t + tr, &n2, &m2), tr);
        } else rc = F3(g->FOGC);
        col = col * (1.0f - fr * 0.85f) + rc * fr;
    }
    return col;
}

// ---------------------------------------------------------------- camera rays
void camray(__constant Glob *g, float sx, float sy, float3 *ro, float3 *rd) {
    float nx = (sx / g->W) * 2 - 1, ny = 1 - (sy / g->H) * 2;
    float aspect = (float)g->W / g->H;
    if (g->ORTHO) {
        *ro = F3(g->CP) + F3(g->CR) * (nx * g->OH * 0.5f * aspect) + F3(g->CU) * (ny * g->OH * 0.5f);
        *rd = F3(g->CF);
    } else {
        float th = tan(g->FOV * 0.5f);
        *ro = F3(g->CP);
        *rd = nrm(F3(g->CF) + F3(g->CR) * (nx * th * aspect) + F3(g->CU) * (ny * th));
    }
}

inline float fogdens(__constant Glob *g, float3 p) {
    float h = fmax(p.y - g->FOGH0, 0);
    return g->FOGD * exp(-h * g->FOGHF);
}

__constant float BAYER4[16] = {0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5};

#define CTX_ARGS __constant Glob *g, __global const Prim *P, __global const Decal *D, __global const Mat *M, \
    __global const Light *L, __global const Tex *T, __global const float *TX, \
    __global const int *GSTART, __global const int *GCOUNT, __global const int *GLIST
#define CTX_INIT Ctx C; C.g = g; C.P = P; C.D = D; C.M = M; C.L = L; C.T = T; C.TX = TX; \
    C.GSTART = GSTART; C.GCOUNT = GCOUNT; C.GLIST = GLIST; C.inner = 0; C.prim = -1;

// one work item per pixel, for a band of rows starting at y0
__kernel void surface(CTX_ARGS, int y0, __global float *S, __global float *DEP) {
    CTX_INIT
    int x = get_global_id(0), y = y0 + get_global_id(1);
    if (x >= g->W || y >= g->H) return;
    float3 ro, rd; camray(g, x + 0.5f, y + 0.5f, &ro, &rd);
    float t; float3 p; int m;
    int i = y * g->W + x;
    if (trace(&C, ro, rd, g->FOGMAX, 400, &t, &p, &m)) {
        float3 c = shade0(&C, p, rd, m, C.prim, t);
        vstore4((float4)(c, 1.0f), i, S);
        DEP[i] = t;
    } else {
        vstore4((float4)(F3(g->FOGC), 0.0f), i, S);
        DEP[i] = g->FOGMAX;
    }
}

__kernel void volume(CTX_ARGS, int y0, __global const float *DEP, __global float *VO) {
    CTX_INIT
    int VS = g->VS, vw = g->W / VS, vh = g->H / VS;
    int x = get_global_id(0), y = y0 + get_global_id(1);
    if (x >= vw || y >= vh) return;
    float tend = g->FOGMAX;
    for (int j = 0; j < VS; j++) for (int i = 0; i < VS; i++) {
        float dd = DEP[(y * VS + j) * g->W + x * VS + i]; if (dd < tend) tend = dd;
    }
    float3 ro, rd; camray(g, (x + 0.5f) * VS, (y + 0.5f) * VS, &ro, &rd);
    int vsteps = g->VSTEPS;
    float dt = tend / vsteps;
    float jit = (BAYER4[(y & 3) * 4 + (x & 3)] + 0.5f) / 16.0f;
    float3 acc = V(0, 0, 0); float Tr = 1.0f;
    for (int s = 0; s < vsteps; s++) {
        float tt = (s + jit) * dt;
        float3 q = ro + rd * tt;
        float dens = fogdens(g, q);
        if (dens <= 1e-6f) continue;
        float3 li = F3(g->FOGC);
        for (int k = 0; k < g->NL; k++) {
            __global const Light *l = L + k;
            if (l->vol <= 0) continue;
            float3 ld; float dist;
            if (l->type == 2) { ld = -F3(l->d); dist = 1e3f; }
            else { float3 dv = F3(l->p) - q; dist = len3(dv); if (dist > l->range) continue; ld = dv * (1.0f / dist); }
            float a = atten(l, dist) * conef(l, -ld);
            if (a < 1e-4f) continue;
            float cth = dot(rd, ld);
            float gg = 0.35f, ph = (1 - gg * gg) / pow(1 + gg * gg - 2 * gg * cth, 1.5f) * 0.25f;
            float sh = 1.0f;
            if (l->volshadow && g->SHADOWS) sh = softshadow(&C, q, ld, fmin(dist, 30.0f) - 0.35f, 30.0f);
            li = li + F3(l->col) * (a * ph * sh * l->vol);
        }
        float ext = exp(-dens * dt);
        acc = acc + li * (Tr * (1 - ext));
        Tr *= ext;
    }
    vstore4((float4)(acc, Tr), y * vw + x, VO);
}
