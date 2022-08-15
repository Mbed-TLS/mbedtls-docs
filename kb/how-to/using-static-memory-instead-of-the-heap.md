# Alternative ways of allocating memory in Mbed TLS

In several situations, like when not having an operating system on an embedded platform, there is no real availability of a heap or `calloc()`/`free()`. Mbed TLS still needs some form of dynamic memory allocation to operate the SSL stack. We could just assume the maximum sizes for all structures, but that would consume a lot of memory space. Instead we opted for letting Mbed TLS only use hooks to allocate and free dynamic memory.

This currently gives you two options:

1. Provide your own allocation and freeing functions.
2. Use the buffer allocator feature in Mbed TLS.

To enable the memory allocation layer, define `MBEDTLS_PLATFORM_C` and `MBEDTLS_PLATFORM_MEMORY` in the `config.h` file. See [How do I configure Mbed TLS](/kb/compiling-and-building/how-do-i-configure-mbedtls.md).

If you do not enable the layer, the libc standard `calloc()` and `free()` are used.

## Internals

Internally, there are just two function pointers `mbedtls_calloc()` and `mbedtls_free()` that are called within Mbed TLS for each dynamic memory allocation or de-allocation.

    extern void * (*mbedtls_calloc)( size_t n, size_t size );
    extern void (*mbedtls_free)( void *ptr );

The prototypes for these functions are identical to the `libc` standard `calloc()` and `free()`. Without any further calls, the default `libc` names are assigned to these pointers.

### No libc equivalents

If your system does not have a `libc` equivalent, you will get compile errors as `calloc()` or `free()` cannot be found.

Defining `MBEDTLS_PLATFORM_NO_STD_FUNCTIONS` in the `config.h` file prevents Mbed TLS from ever knowing about those functions.

### Providing your own hooks

If your operating system already provides an alternative to the `libc` allocator functions, you can set them with:

    int mbedtls_platform_set_calloc_free( void * (*calloc_func)( size_t, size_t ),
                                          void (*free_func)( void * ) );

## Using the Mbed TLS buffer allocator

If you want Mbed TLS to allocate everything inside a static buffer, you can enable the buffer allocator by defining `MBEDTLS_MEMORY_BUFFER_ALLOC_C` in the `config.h` file.

Before calling any other Mbed TLS functions, enable the buffer allocator as follows:

    unsigned char memory_buf[100000];
    mbedtls_memory_buffer_alloc_init( memory_buf, sizeof(memory_buf) );

## Security warning

The buffer allocator is a straightforward approach to a dynamic memory allocator. No special heap protection mechanisms have been implemented.

## Using the buffer allocator elsewhere

The buffer allocator itself has no internal dependencies on any of the rest of Mbed TLS. So you can use it within your own codebase as well.

<!-- This guide from Mbed TLS explains how to prevent use of malloc() and free() within Mbed TLS and use your another (more static) dynamic memory allocator. malloc, free, memory allocation, dynamic memory, heap, stack, buffer_alloc -->
