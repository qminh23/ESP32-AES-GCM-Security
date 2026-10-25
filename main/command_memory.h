#pragma once
#include <stdbool.h>
#include <stdint.h>

/* Protocol 3: đo sau HEX, trước hàng đợi GPIO. Heap chỉ tính cấp phát mới;
 * stack_peak chỉ dùng khi stack_status=MEASURED. Loại trừ tác vụ khác và ISR. */
typedef struct {
    uint32_t heap_before, heap_after;
    uint32_t heap_peak, heap_retained, allocations;
    uint32_t stack_free_min, context_bytes, stack_peak;
    /* valid applies to heap tracking only; stack_status qualifies stack_peak. */
    uint32_t stack_status;
    bool valid, aes_enabled;
} command_memory_t;

enum { COMMAND_STACK_UNAVAILABLE, COMMAND_STACK_MEASURED,
       COMMAND_STACK_UNTOUCHED, COMMAND_STACK_SATURATED };

void command_memory_begin(bool aes_enabled, uint32_t context_bytes);
command_memory_t command_memory_end(void);
