# Mbed TLS abstraction layers

## Abstraction layers

> Not all systems are made equal. Some are more equal than others.

The Mbed TLS core allows smooth integration on a wide number of platforms. It provides a number of abstraction layers that make this possible.

## Standard function abstraction

These are standard functions from libc that are always needed. However, they will have different implementations and behave differently on some platforms.

Examples: `calloc()`, `free()`, `printf()` and `fprintf()`.

These standard functions are abstracted in the **platform layer**. The layer core is enabled by default in `mbedtls_config.h` with `MBEDTLS_PLATFORM_C`, and allows the runtime customization of the relevant function.

The `MBEDTLS_PLATFORM_XXX` defined in `mbedtls_config.h` enables support for abstracting different functions.

For example, after enabling `MBEDTLS_PLATFORM_PRINTF_ALT`, you can set an alternative for `printf()` by calling `mbedtls_platform_set_printf()`.

## Additional function abstraction

These are additional functions from external libraries or OS that are needed only in some circumstances, for example, threading library support.

Examples: threading.

These abstractions are implemented in their own module and enabled or disabled with a single define, for example, `MBEDTLS_THREADING_C` in `mbedtls_config.h`. They may also require additional configuration options. The threading library, for example, requires you to indicate which threading library you are using: pthread or an alternative.

## Implementation abstraction

These are abstractions for functions that we already provide an implementation for. However, some users may want to use their own versions instead, for example, those optimized for their platforms.

Examples: AES, MD5 and Timing.

To enable an implementation abstraction:
- You'll need to enable the relevant macro: `MBEDTLS_XXX_ALT` in `mbedtls_config.h`.
- Provide a custom header, named: `xxx_alt.h`.
- Provide an implementation.

You can also opt to provide your own version of the `core` function of a module, rather than the whole module.

Examples: AES setkey, AES block encrypt and decrypt, and SHA process.

To enable an implementation abstraction, you must provide your own implementation of the relevant function with the same prototype as the default implementation.

<!--",abstraction-layers,"Explanation on the different abstraction layers that Mbed TLS provides, such as for memory allocation. threading and cryptographic implementations.",,"abstraction, threading, memory, printf",published,"2014-02-06 13:04:00",1,2425,"2017-04-23 15:02:00","Paul Bakker"-->
