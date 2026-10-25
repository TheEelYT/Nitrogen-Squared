/* Original compatibility code for the pinned runtime's two GNU-style int
 * atomic calls in gpu_gl_renderer.c. This is not a general libatomic shim. */
#ifndef NITROGEN_MSVC_ATOMICS_H
#define NITROGEN_MSVC_ATOMICS_H

#if defined(_MSC_VER) && !defined(__clang__) && !defined(__cplusplus)
#include <intrin.h>
#include <limits.h>

_Static_assert(sizeof(int) == 4 && sizeof(long) == 4 && INT_MAX == LONG_MAX,
               "The MSVC atomic adapter requires 32-bit int and long");

static __forceinline void nitrogen_atomic_store_int(volatile int *object, int value)
{
    (void)_InterlockedExchange((volatile long *)object, (long)value);
}

static __forceinline int nitrogen_atomic_load_int(volatile int *object)
{
    return (int)_InterlockedCompareExchange((volatile long *)object, 0, 0);
}

/* The unsuffixed Interlocked intrinsics provide full memory barriers, which
 * satisfy the renderer's release store and acquire load. Keep every access to
 * the flag atomic, including loads, and evaluate each argument only once. */
#ifndef __ATOMIC_ACQUIRE
#define __ATOMIC_ACQUIRE 2
#endif
#ifndef __ATOMIC_RELEASE
#define __ATOMIC_RELEASE 3
#endif
#define __atomic_store_n(object, value, order) \
    ((void)(order), nitrogen_atomic_store_int((object), (value)))
#define __atomic_load_n(object, order) \
    ((void)(order), nitrogen_atomic_load_int((object)))
#endif

#endif
