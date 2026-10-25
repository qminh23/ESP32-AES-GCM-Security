#include "command_memory.h"
#include <stdatomic.h>
#include <stddef.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_cpu.h"
#include "esp_heap_caps.h"

#ifndef CONFIG_HEAP_USE_HOOKS
#error "Command memory measurement requires CONFIG_HEAP_USE_HOOKS=y"
#endif

/* MQTT là tác vụ duy nhất ghi mẫu; hooks không cấp phát, log hoặc khóa. */
#define TRACKED_BLOCKS 32
static struct { void *ptr; size_t size; } s_blocks[TRACKED_BLOCKS];
static _Atomic(TaskHandle_t) s_owner;
static command_memory_t s_sample;

/* Tô vùng stack dưới SP trên Xtensa. Chưa chạm hoặc chạm đáy: không có đỉnh chính xác. */
#define STACK_PROBE_GUARD 64
#define STACK_PROBE_WINDOW_MAX 2048
#define STACK_PROBE_FILL 0xa5u
static uint8_t *s_window_low, *s_window_high, *s_sp_begin;

static void stack_probe_begin(void) {
    uint32_t free_bytes = uxTaskGetStackHighWaterMark(NULL);
    uint8_t *sp = (uint8_t *)esp_cpu_get_sp();
    s_window_low = s_window_high = s_sp_begin = NULL;
    if (free_bytes <= 2 * STACK_PROBE_GUARD + 64) return;
    uint32_t span = free_bytes - 2 * STACK_PROBE_GUARD;
    if (span > STACK_PROBE_WINDOW_MAX) span = STACK_PROBE_WINDOW_MAX;
    uintptr_t low = ((uintptr_t)sp - STACK_PROBE_GUARD - span) & ~(uintptr_t)3;
    uintptr_t high = ((uintptr_t)sp - STACK_PROBE_GUARD) & ~(uintptr_t)3;
    if (high <= low) return;
    volatile uint32_t *word = (volatile uint32_t *)low;
    for (; (uintptr_t)word < high; ++word) *word = 0xa5a5a5a5u;
    s_sp_begin = sp;
    s_window_low = (uint8_t *)low;
    s_window_high = (uint8_t *)high;
}

static uint32_t stack_probe_end(uint32_t *peak) {
    if (!s_window_low) return COMMAND_STACK_UNAVAILABLE;
    volatile uint8_t *p = s_window_low;
    while (p < s_window_high && *p == STACK_PROBE_FILL) ++p;
    if (p == s_window_low) return COMMAND_STACK_SATURATED;
    if (p == s_window_high) return COMMAND_STACK_UNTOUCHED;
    *peak = (uint32_t)(s_sp_begin - (const uint8_t *)p);
    return COMMAND_STACK_MEASURED;
}

/* Thuộc tính IRAM kế thừa từ esp_heap_caps.h. */
void esp_heap_trace_alloc_hook(void *ptr, size_t size, uint32_t caps) {
    (void)caps;
    TaskHandle_t owner = atomic_load_explicit(&s_owner, memory_order_relaxed);
    if (!owner || !ptr || xPortInIsrContext() || xTaskGetCurrentTaskHandle() != owner) return;
    /* Không hỗ trợ realloc tại chỗ: loại mẫu để tránh đếm trùng. */
    for (unsigned i = 0; i < TRACKED_BLOCKS; ++i) {
        if (s_blocks[i].ptr == ptr) { s_sample.valid = false; return; }
    }
    for (unsigned i = 0; i < TRACKED_BLOCKS; ++i) {
        if (!s_blocks[i].ptr) {
            s_blocks[i].ptr = ptr;
            s_blocks[i].size = size;
            s_sample.heap_retained += size;
            s_sample.allocations++;
            if (s_sample.heap_retained > s_sample.heap_peak)
                s_sample.heap_peak = s_sample.heap_retained;
            return;
        }
    }
    s_sample.valid = false; /* Never report an underestimated peak as valid. */
}

void esp_heap_trace_free_hook(void *ptr) {
    TaskHandle_t owner = atomic_load_explicit(&s_owner, memory_order_relaxed);
    if (!owner || !ptr || xPortInIsrContext() || xTaskGetCurrentTaskHandle() != owner) return;
    for (unsigned i = 0; i < TRACKED_BLOCKS; ++i) {
        if (s_blocks[i].ptr == ptr) {
            s_sample.heap_retained -= s_blocks[i].size;
            s_blocks[i].ptr = NULL;
            return;
        }
    }
}

void command_memory_begin(bool aes_enabled, uint32_t context_bytes) {
    atomic_store(&s_owner, NULL);
    memset(s_blocks, 0, sizeof(s_blocks));
    s_sample = (command_memory_t){.valid = true, .aes_enabled = aes_enabled,
        .context_bytes = context_bytes,
        .heap_before = heap_caps_get_free_size(MALLOC_CAP_8BIT)};
    stack_probe_begin();
    atomic_store(&s_owner, xTaskGetCurrentTaskHandle());
}

command_memory_t command_memory_end(void) {
    TaskHandle_t owner = atomic_load(&s_owner);
    if (!owner || owner != xTaskGetCurrentTaskHandle()) return (command_memory_t){0};
    atomic_store(&s_owner, NULL);
    uint32_t peak = 0;
    s_sample.stack_status = stack_probe_end(&peak);
    s_sample.stack_peak = peak;
    s_sample.heap_after = heap_caps_get_free_size(MALLOC_CAP_8BIT);
    /* Watermark tính bằng byte; không so với số tích lũy của v1. */
    s_sample.stack_free_min = uxTaskGetStackHighWaterMark(NULL);
    return s_sample;
}
