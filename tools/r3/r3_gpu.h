// r3_gpu.h: runs r3's surface and volumetric passes on the GPU through OpenCL (kernels in r3.cl).
// Included by r3.c. OpenCL.dll comes with the graphics driver and is loaded at run time, so r3 still
// builds and runs (on the CPU) on machines without it. Probe mode always runs on the CPU.
//
// gpu_render() returns 0 on success; on any failure it prints why and returns nonzero, and r3 falls back
// to the CPU passes.

#ifdef _WIN32
#include <windows.h>
#define CLAPI __stdcall
#else
#include <dlfcn.h>
#include <time.h>
#define CLAPI
#endif

// the handful of OpenCL 1.2 declarations r3 needs (no SDK headers required)
typedef int32_t cl_int; typedef uint32_t cl_uint; typedef uint64_t cl_ulong;
typedef void *cl_platform_id, *cl_device_id, *cl_context, *cl_command_queue, *cl_mem, *cl_program, *cl_kernel, *cl_event;
#define CL_DEVICE_TYPE_GPU (1 << 2)
#define CL_MEM_READ_WRITE (1 << 0)
#define CL_MEM_READ_ONLY (1 << 2)
#define CL_MEM_COPY_HOST_PTR (1 << 5)
#define CL_DEVICE_NAME 0x102B
#define CL_PLATFORM_NAME 0x0902
#define CL_PROGRAM_BUILD_LOG 0x1183

static struct {
    cl_int (CLAPI *GetPlatformIDs)(cl_uint, cl_platform_id *, cl_uint *);
    cl_int (CLAPI *GetDeviceIDs)(cl_platform_id, cl_ulong, cl_uint, cl_device_id *, cl_uint *);
    cl_int (CLAPI *GetDeviceInfo)(cl_device_id, cl_uint, size_t, void *, size_t *);
    cl_context (CLAPI *CreateContext)(const intptr_t *, cl_uint, const cl_device_id *, void *, void *, cl_int *);
    cl_command_queue (CLAPI *CreateCommandQueue)(cl_context, cl_device_id, cl_ulong, cl_int *);
    cl_program (CLAPI *CreateProgramWithSource)(cl_context, cl_uint, const char **, const size_t *, cl_int *);
    cl_int (CLAPI *BuildProgram)(cl_program, cl_uint, const cl_device_id *, const char *, void *, void *);
    cl_int (CLAPI *GetProgramBuildInfo)(cl_program, cl_device_id, cl_uint, size_t, void *, size_t *);
    cl_kernel (CLAPI *CreateKernel)(cl_program, const char *, cl_int *);
    cl_mem (CLAPI *CreateBuffer)(cl_context, cl_ulong, size_t, void *, cl_int *);
    cl_int (CLAPI *SetKernelArg)(cl_kernel, cl_uint, size_t, const void *);
    cl_int (CLAPI *EnqueueNDRangeKernel)(cl_command_queue, cl_kernel, cl_uint, const size_t *, const size_t *,
                                         const size_t *, cl_uint, const cl_event *, cl_event *);
    cl_int (CLAPI *EnqueueReadBuffer)(cl_command_queue, cl_mem, cl_uint, size_t, size_t, void *, cl_uint,
                                      const cl_event *, cl_event *);
    cl_int (CLAPI *Finish)(cl_command_queue);
} cl;

static int cl_load(void) {
#ifdef _WIN32
    HMODULE h = LoadLibraryA("OpenCL.dll");
#else
    void *h = dlopen("libOpenCL.so.1", RTLD_NOW); if (!h) h = dlopen("libOpenCL.so", RTLD_NOW);
#endif
    if (!h) return 0;
    void **f = (void **)&cl;
    const char *names[] = {"GetPlatformIDs", "GetDeviceIDs", "GetDeviceInfo", "CreateContext", "CreateCommandQueue",
        "CreateProgramWithSource", "BuildProgram", "GetProgramBuildInfo", "CreateKernel", "CreateBuffer",
        "SetKernelArg", "EnqueueNDRangeKernel", "EnqueueReadBuffer", "Finish"};
    for (int i = 0; i < (int)(sizeof names / sizeof *names); i++) {
        char nm[64]; snprintf(nm, sizeof nm, "cl%s", names[i]);
#ifdef _WIN32
        f[i] = (void *)GetProcAddress(h, nm);
#else
        f[i] = dlsym(h, nm);
#endif
        if (!f[i]) return 0;
    }
    return 1;
}

// device-side records (all 4-byte fields, same layout as the structs in r3.cl)
typedef struct {
    int type, mat, op; float k; float a[3], b[3]; float ra, rb; float R[9]; float c[3], r[3];
    int clip; float cn[3]; float co; float shell; int clip2; float cn2[3]; float co2; int inmat; float bc[3]; float br;
} GPrim;
typedef struct { int from, to, np; float n[6][3]; float o[6]; float feather; } GDecal;
typedef struct {
    float col[3]; float spec, shin, namp, nscale, bump, bscale, wrap, aniso;
    float emis[3]; float refl, rough; int tex, texmode, texmap; float texscale, texemis, ripple;
} GMat;
typedef struct { int type; float p[3], d[3], col[3]; float range, cosi, coso; int shadow; float vol; int volshadow; float soft; } GLight;
typedef struct { int w, h, off; } GTex;
typedef struct {
    int W, H, ORTHO, VS, VSTEPS, REFL, SHADOWS, NL, ND, GX, GY, GZ, pad0, pad1;
    float CP[3], CF[3], CR[3], CU[3]; float FOV, OH;
    float SKY[3], BOUNCE[3], FOGC[3]; float FOGD, FOGH0, FOGHF, FOGMAX, AOS;
    float GMIN[3], GMAX[3]; float GCS;
} GGlob;

#define C3(dst, v) ((dst)[0] = (v).x, (dst)[1] = (v).y, (dst)[2] = (v).z)

static char *read_text(const char *path) {
    FILE *f = fopen(path, "rb"); if (!f) return NULL;
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    char *s = malloc(n + 1); if (fread(s, 1, n, f) != (size_t)n) { fclose(f); free(s); return NULL; }
    s[n] = 0; fclose(f); return s;
}

static double now_s(void) {
#ifdef _WIN32
    LARGE_INTEGER c, fq; QueryPerformanceCounter(&c); QueryPerformanceFrequency(&fq); return (double)c.QuadPart / fq.QuadPart;
#else
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + ts.tv_nsec * 1e-9;
#endif
}

// Enqueue `kern` over a w x h grid in bands of rows. Each band is short, so no single dispatch runs long
// enough to trip the Windows GPU watchdog (TDR, 2 s); the band height adapts to keep each one ~0.15 s.
static int run_bands(cl_command_queue q, cl_kernel kern, int yarg, int w, int h) {
    int band = 8;
    for (int y0 = 0; y0 < h;) {
        int rows = band < h - y0 ? band : h - y0;
        size_t gs[2] = {(size_t)(w + 15) / 16 * 16, (size_t)rows}, ls[2] = {16, 1};
        cl.SetKernelArg(kern, yarg, sizeof(int), &y0);
        double t0 = now_s();
        cl_int e = cl.EnqueueNDRangeKernel(q, kern, 2, NULL, gs, ls, 0, NULL, NULL);
        if (e) { fprintf(stderr, "r3 gpu: enqueue failed (%d)\n", e); return 1; }
        if ((e = cl.Finish(q))) { fprintf(stderr, "r3 gpu: kernel failed (%d)\n", e); return 1; }
        double dt = now_s() - t0;
        y0 += rows;
        int nb = dt > 1e-4 ? (int)(band * 0.15 / dt) : band * 4;
        if (nb > band * 4) nb = band * 4;
        if (nb < 1) nb = 1;
        band = nb;
    }
    return 0;
}

static int gpu_render(const char *exe, float *S, float *DEP, float *VO, int VSTEPS) {
    if (!cl_load()) { fprintf(stderr, "r3 gpu: no OpenCL.dll\n"); return 1; }
    cl_platform_id plats[8]; cl_uint np = 0;
    if (cl.GetPlatformIDs(8, plats, &np) || !np) { fprintf(stderr, "r3 gpu: no OpenCL platform\n"); return 1; }
    // the first GPU on any platform, preferring a discrete NVIDIA/AMD card over integrated graphics
    cl_device_id dev = NULL; char dname[256] = "";
    for (int pass = 0; pass < 2 && !dev; pass++)
        for (cl_uint i = 0; i < np && !dev; i++) {
            cl_device_id d; cl_uint nd = 0;
            if (cl.GetDeviceIDs(plats[i], CL_DEVICE_TYPE_GPU, 1, &d, &nd) || !nd) continue;
            char nm[256] = ""; cl.GetDeviceInfo(d, CL_DEVICE_NAME, sizeof nm, nm, NULL);
            if (pass == 0 && strstr(nm, "Intel")) continue;
            dev = d; strcpy(dname, nm);
        }
    if (!dev) { fprintf(stderr, "r3 gpu: no OpenCL GPU\n"); return 1; }
    cl_int e;
    cl_context ctx = cl.CreateContext(NULL, 1, &dev, NULL, NULL, &e); if (e) return 1;
    cl_command_queue q = cl.CreateCommandQueue(ctx, dev, 0, &e); if (e) return 1;

    // the kernel source sits next to the executable
    char path[1024]; snprintf(path, sizeof path, "%s", exe);
    char *slash = strrchr(path, '\\'), *s2 = strrchr(path, '/'); if (s2 > slash) slash = s2;
    if (slash) slash[1] = 0; else path[0] = 0;
    strncat(path, "r3.cl", sizeof path - strlen(path) - 1);
    char *src = read_text(path);
    if (!src) { fprintf(stderr, "r3 gpu: can't read %s\n", path); return 1; }
    double t0 = now_s();
    cl_program prog = cl.CreateProgramWithSource(ctx, 1, (const char **)&src, NULL, &e); if (e) return 1;
    if (cl.BuildProgram(prog, 1, &dev, "-cl-std=CL1.2 -cl-mad-enable", NULL, NULL)) {
        size_t n = 0; cl.GetProgramBuildInfo(prog, dev, CL_PROGRAM_BUILD_LOG, 0, NULL, &n);
        char *log = malloc(n + 1); cl.GetProgramBuildInfo(prog, dev, CL_PROGRAM_BUILD_LOG, n, log, NULL); log[n] = 0;
        fprintf(stderr, "r3 gpu: r3.cl failed to build:\n%s\n", log); return 1;
    }
    fprintf(stderr, "r3: rendering on the GPU (%s), kernels built in %.1f s\n", dname, now_s() - t0);

    // ---- scene data
    GGlob g; memset(&g, 0, sizeof g);
    g.W = W; g.H = H; g.ORTHO = ORTHO; g.VS = VS; g.VSTEPS = VSTEPS; g.REFL = REFL; g.SHADOWS = SHADOWS;
    g.NL = NL; g.ND = ND; g.GX = GX; g.GY = GY; g.GZ = GZ;
    C3(g.CP, CP); C3(g.CF, CF); C3(g.CR, CR); C3(g.CU, CU); g.FOV = FOV; g.OH = OH;
    C3(g.SKY, SKY); C3(g.BOUNCE, BOUNCE); C3(g.FOGC, FOGC);
    g.FOGD = FOGD; g.FOGH0 = FOGH0; g.FOGHF = FOGHF; g.FOGMAX = FOGMAX; g.AOS = AOS;
    C3(g.GMIN, GMIN); C3(g.GMAX, GMAX); g.GCS = GCS;
    GPrim *gp = calloc(NP + 1, sizeof(GPrim));
    for (int i = 0; i < NP; i++) {
        Prim *p = &P[i]; GPrim *o = &gp[i];
        o->type = p->type; o->mat = p->mat; o->op = p->op; o->k = p->k; C3(o->a, p->a); C3(o->b, p->b);
        o->ra = p->ra; o->rb = p->rb; memcpy(o->R, p->R, sizeof o->R); C3(o->c, p->c); C3(o->r, p->r);
        o->clip = p->clip; C3(o->cn, p->cn); o->co = p->co; o->shell = p->shell; o->clip2 = p->clip2;
        C3(o->cn2, p->cn2); o->co2 = p->co2; o->inmat = p->inmat; C3(o->bc, p->bc); o->br = p->br;
    }
    GDecal *gd = calloc(ND + 1, sizeof(GDecal));
    for (int i = 0; i < ND; i++) {
        gd[i].from = D[i].from; gd[i].to = D[i].to; gd[i].np = D[i].np; gd[i].feather = D[i].feather;
        for (int j = 0; j < 6; j++) { C3(gd[i].n[j], D[i].n[j]); gd[i].o[j] = D[i].o[j]; }
    }
    GMat *gm = calloc(NM + 1, sizeof(GMat));
    for (int i = 0; i < NM; i++) {
        Mat *m = &M[i]; GMat *o = &gm[i];
        C3(o->col, m->col); o->spec = m->spec; o->shin = m->shin; o->namp = m->namp; o->nscale = m->nscale;
        o->bump = m->bump; o->bscale = m->bscale; o->wrap = m->wrap; o->aniso = m->aniso; C3(o->emis, m->emis);
        o->refl = m->refl; o->rough = m->rough; o->tex = m->tex; o->texmode = m->texmode; o->texmap = m->texmap;
        o->texscale = m->texscale; o->texemis = m->texemis; o->ripple = m->ripple;
    }
    GLight *gl = calloc(NL + 1, sizeof(GLight));
    for (int i = 0; i < NL; i++) {
        Light *l = &L[i]; GLight *o = &gl[i];
        o->type = l->type; C3(o->p, l->p); C3(o->d, l->d); C3(o->col, l->col); o->range = l->range;
        o->cosi = l->cosi; o->coso = l->coso; o->shadow = l->shadow; o->vol = l->vol; o->volshadow = l->volshadow;
        o->soft = l->soft;
    }
    GTex *gt = calloc(NT + 1, sizeof(GTex)); size_t ntx = 0;
    for (int i = 0; i < NT; i++) { gt[i].w = T[i].w; gt[i].h = T[i].h; gt[i].off = (int)ntx; ntx += (size_t)T[i].w * T[i].h; }
    float *tx = malloc(sizeof(float) * 4 * (ntx + 1));
    for (int i = 0; i < NT; i++) memcpy(tx + (size_t)gt[i].off * 4, T[i].px, sizeof(float) * 4 * T[i].w * T[i].h);
    int nc = GX * GY * GZ, nl = GSTART[nc - 1] + GCOUNT[nc - 1];

#define BUF(ptr, bytes) cl.CreateBuffer(ctx, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR, (bytes), (ptr), &e)
    cl_mem bg = BUF(&g, sizeof g), bp = BUF(gp, sizeof(GPrim) * (NP + 1)), bd = BUF(gd, sizeof(GDecal) * (ND + 1)),
           bm = BUF(gm, sizeof(GMat) * (NM + 1)), bl = BUF(gl, sizeof(GLight) * (NL + 1)),
           bt = BUF(gt, sizeof(GTex) * (NT + 1)), btx = BUF(tx, sizeof(float) * 4 * (ntx + 1)),
           bs = BUF(GSTART, sizeof(int) * nc), bc = BUF(GCOUNT, sizeof(int) * nc), bli = BUF(GLIST, sizeof(int) * (nl + 1));
    int n = W * H;
    cl_mem bS = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, sizeof(float) * 4 * n, NULL, &e);
    cl_mem bD = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, sizeof(float) * n, NULL, &e);
    if (e) { fprintf(stderr, "r3 gpu: out of GPU memory\n"); return 1; }
    cl_mem ctxbufs[10] = {bg, bp, bd, bm, bl, bt, btx, bs, bc, bli};

    // ---- surface pass
    cl_kernel ks = cl.CreateKernel(prog, "surface", &e); if (e) return 1;
    for (int i = 0; i < 10; i++) cl.SetKernelArg(ks, i, sizeof(cl_mem), &ctxbufs[i]);
    cl.SetKernelArg(ks, 11, sizeof(cl_mem), &bS); cl.SetKernelArg(ks, 12, sizeof(cl_mem), &bD);
    t0 = now_s();
    if (run_bands(q, ks, 10, W, H)) return 1;
    fprintf(stderr, "r3: surface pass %.1f s\n", now_s() - t0);
    if (cl.EnqueueReadBuffer(q, bS, 1, 0, sizeof(float) * 4 * n, S, 0, NULL, NULL)) return 1;
    if (cl.EnqueueReadBuffer(q, bD, 1, 0, sizeof(float) * n, DEP, 0, NULL, NULL)) return 1;

    // ---- volumetric pass
    if (VO) {
        int vw = W / VS, vh = H / VS;
        cl_mem bV = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, sizeof(float) * 4 * vw * vh, NULL, &e); if (e) return 1;
        cl_kernel kv = cl.CreateKernel(prog, "volume", &e); if (e) return 1;
        for (int i = 0; i < 10; i++) cl.SetKernelArg(kv, i, sizeof(cl_mem), &ctxbufs[i]);
        cl.SetKernelArg(kv, 11, sizeof(cl_mem), &bD); cl.SetKernelArg(kv, 12, sizeof(cl_mem), &bV);
        t0 = now_s();
        if (run_bands(q, kv, 10, vw, vh)) return 1;
        fprintf(stderr, "r3: volumetric pass %.1f s\n", now_s() - t0);
        if (cl.EnqueueReadBuffer(q, bV, 1, 0, sizeof(float) * 4 * vw * vh, VO, 0, NULL, NULL)) return 1;
    }
    return 0;   // the process exits right after, which frees everything
}
