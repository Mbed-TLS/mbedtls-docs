# Porting Mbed TLS to a new environment or OS

Mbed TLS is portable across different architectures and runtime environments, and can execute on a variety of different operating systems or bare-metal ports. Using C in a generic way ensures the portability of the architecture, and minimizing platform dependencies allows for environment and architecture independence. Doing this reduces the amount of environment - or OS-dependent code, and cleanly isolates platform-specific code from the highly portable core so you can easily replace the platform code.

This page explains how to port Mbed TLS to a new environment.

<span class="notes">**Note:** This article is about porting Mbed TLS to a new runtime environment, not to a new hardware platform. It only covers the library, not the Mbed TLS example programs nor the test suites, which have different system requirements.</span>

## Overview

Mbed TLS has a modular design. Many of the modules are completely independent of any runtime, environment, or other module dependencies, with the exception of [those dependent on the C library](/kb/development/what-external-dependencies-does-mbedtls-rely-on.md).

The only parts of the library that potentially interact with the environment are:

* The network module `net_sockets.c` that can be disabled and replaced with a separate network stack. This can mean any transport layer stack that uses Mbed TLS.
* The timing module `timing.c` that can be disabled and replaced to suit the underlying OS or hardware drivers.
* Default sources of entropy in the entropy module and additional sources. You can register these.
* Optional functions that access a file system.
* Functions that need the current time from a real-time clock. You can disable them, although that limits what validation is possible for certificates.
* Functions that print messages, generally used for debug and diagnosis. You can disable or replace them to output messages to another platform-specific debug.

In short, in order to compile Mbed TLS for a bare-metal environment which already has a standard C library, [configure your build](/kb/compiling-and-building/how-do-i-configure-mbedtls.md) by disabling `MBEDTLS_NET_C`, `MBEDTLS_TIMING_C` and `MBEDTLS_ENTROPY_PLATFORM`, and potentially `MBEDTLS_FS_IO`, `MBEDTLS_HAVE_TIME_DATE` and `MBEDTLS_HAVE_TIME`.

This is more thoroughly documented in [`config.h`](/api/config_8h.html).

The following sections give more detail on how to replace the missing parts.

## Networking

The provided network module `net_sockets.c` works on Windows and Unix systems that implement the BSD sockets API. It is optionally used by the SSL/TLS module through callback functions, and can be disabled at compilation without affecting the rest of the library.

The callbacks can be replaced by coding your own functions for blocking or non-blocking write and read with optional timeout, based on the network or transport layer stack of your choice. Substitute functions must match the API expected by the function [`mbedtls_ssl_set_bio()`](/api/ssl_8h.html).

## Timing

The provided timing module `timing.c` works on Windows, Linux and BSD (including OS X). It is only optionally used by the SSL/TLS module through callback functions for DTLS and can be disabled at compilation without affecting the rest of the library.

If you are not using DTLS, you do not need a timing function. If you are using DTLS, you need to write your own timer callbacks suitable to pass to the function [`mbedtls_ssl_set_timer_cb()`](/api/ssl_8h.html). This is discussed in more detail in our [DTLS tutorial](/kb/how-to/dtls-tutorial.md).

## Default entropy sources

The entropy pool, part of the RNG module, collects and securely mixes entropy from a variety of sources. On Windows and different Unix platforms that provide `/dev/urandom`, a default OS-based source is registered. You can disable it at compilation without affecting the rest of the library.

This source can be replaced by coding one or more entropy-collection functions that implement the API expected by the function [`mbedtls_entropy_add_source()`](/api/entropy_8h.html) and registering it with that function at runtime, or if it is based on a hardware source, at compilation time with `MBEDTLS_ENTROPY_HARDWARE_ALT`.

Please note that, for security reasons, the entropy module will refuse to output anything until a declared-strong source has been registered.

<span class="warnings">**Warning:** Evaluating the strength of the sources provided is the responsibility of those doing the platform port.</span>

## Hardware Acceleration

You can substitute alternative implementations of cryptographic primitives in most modules that implement them to take advantage of the hardware acceleration that may be present. This can be achieved by defining the appropriate `MBEDTLS_*_ALT` preprocessor symbol for each module that needs to be replaced. For example `MBEDTLS_AES_ALT` may be defined to replace the whole AES API with a hardware accelerated AES driver, and `MBEDTLS_AES_ENCRYPT_ALT` may be defined for replacing only the AES block encrypt functionality. For more information, see the [hardware accelerator guidelines](/kb/development/hw_acc_guidelines.md).

## File system access

Several modules include functions that access the file system. You can disable all of them at compilation time without affecting the rest of the library.

Every function that accesses the file system is only a convenience wrapper around a function that does the same job with memory buffers, so there is nothing to replace. Use the functions that work on buffers.

## Real time clock

A few modules optionally access the current time, either to measure time intervals, or to know the absolute current time and date. You can disable those features at compilation time without affecting the rest of the library.

Every function that measures intervals has an alternate version of the code to provide similar functionality when time is not available (for example, rotating keys based on the number of uses rather than elapsed time). Absolute time and date are only used in X.509 in order to check the validity period of certificates. If time and date are not available, then this check is skipped.

<span class="warnings">**Warning:** Depending on how you use X.509 certificates to secure your platform, this could be a serious security risk.</span>

## Diagnostic output

In the library, the only functions that print messages (using `printf()`) are the self-test functions. These can be disabled at compilation time (`MBEDTLS_SELF_TEST`) without affecting the rest of the library.

Alternatively, `printf()` can easily be replaced with your own printing function, either by enabling `MBEDTLS_PLATFORM_PRINTF_ALT` at compilation time and then using `mbedtls_platform_set_printf()` at runtime, or by using `MBEDTLS_PLATFORM_PRINTF_MACRO` at compilation time.

### Platform setup and teardown

In some cases, the underlying hardware requires explicit initialization, before the hardware specific functions can operate properly.
Special deinitialization operations may be required afterwards as well.
To account for that, the `mbedtls_platform_setup()` and `mbedtls_platform_teardown()` functions are available in the Mbed TLS API.
By default they do not perform any actions.
However, you can provide your own implementation in order to give third parties integrating Mbed TLS into their own platforms a uniform way of initializing any underlying hardware or accelerators.
As such, to aid portability of application code that uses Mbed TLS across platforms, we recommend you to use these functions.
The code changes that are needed are discussed below.

For a target device to provide custom setup and teardown functions, you must define the macro `MBEDTLS_PLATFORM_SETUP_TEARDOWN_ALT` as shown below:
```
#define MBEDTLS_PLATFORM_SETUP_TEARDOWN_ALT
```
Then, you must provide a "platform_alt.h" header file, defining a platform context structure:
```
typedef struct {
    ...
}
mbedtls_platform_context;
```
Finally, you must provide implementations for the platform specific setup and teardown operations:
```
#if defined(MBEDTLS_PLATFORM_SETUP_TEARDOWN_ALT)
int mbedtls_platform_setup( mbedtls_platform_context *ctx )
{
    ...
}

void mbedtls_platform_teardown( mbedtls_platform_context *ctx )
{
    ...
}
#endif
```

Note that the setup and teardown functions must be called, respectively, before and after any other calls to the Mbed TLS API are made, as shown in the example:

```
 #include "mbedtls/platform.h"
...

int main()
{
    int ret;

#if defined(MBEDTLS_PLATFORM_C)
    mbedtls_platform_context platform_ctx;
#endif

    ...

#if defined(MBEDTLS_PLATFORM_C)
    if( ( ret = mbedtls_platform_setup( &platform_ctx ) ) != 0 )
    {
        // Error handling
    }
#endif

    // Your code goes here

    ...

#if defined(MBEDTLS_PLATFORM_C)
    mbedtls_platform_teardown( &platform_ctx );
#endif

    return( 0 );
}
```

<!---",how-do-i-port-mbed-tls-to-a-new-environment-OS,"How to port Mbed TLS to a new environment, architecture or OS",,"port, porting, environment, architecture, library, OS, system, network, timing, file system, entropy, platform",published,"2016-02-17 09:50:00",2,16866,"2017-04-23 14:37:00","Manuel PÃ©gouriÃ©-Gonnard"--->
