# Thread safety and multithreading: concurrency issues

## Thread safety

You can use Arm Mbed TLS in threaded and nonthreaded environments. To keep Mbed TLS thread-safe, it is important to remember a few things.

First, most functions use an explicit context. Most of the time, as long as threads do not share this context, you're safe. However, sometimes threads can share a context indirectly. For example, an SSL context can point to an RSA context (the private key).

The default philosophy is that a single thread should only use or access one context at a same time, unless:

- The documentation for the functions that access the shared context explicitly states the function is thread-safe, or
- You perform explicit locking yourself (perhaps in a wrapper function).

## Thread safety with different versions

Mbed TLS has a generic threading layer that handles default locks and mutexes for the user and abstracts the threading layer to allow easy pluging in any thread-library.

Defining **MBEDTLS_THREADING_C** in *config.h* enables this threading layer. Please see [How do I configure Mbed TLS](https://tls.mbed.org/kb/compiling-and-building/how-do-i-configure-mbedtls) for more information. It is not enabled by default; you also need to pick an underlying threading library. We provide built-in support for `pthread` with **MBEDTS_THREADING_PTHREAD**. You can also plug any other thread-library with **MBEDTLS_THREADING_ALT** and call `mbedtls_threading_set_alt()` at the beginning of your program and `mbedtls_threading_free_alt()` at the end.

## Status of various contexts and associated functions

All contexts have associated `_init()` and `_free()` functions. For contexts that include mutexes, these functions create and initialize the mutex and then free and destroy it. If you share a context between threads, you need to call these functions only from the main thread, at the beginning and end of the context's lifetime.

Mbed TLS currently provides automatic locking (when the threading layer is enabled) for relevant functions in the following modules (unless indicated otherwise):

- RSA.
- The SSL cache callbacks provided in `ssl_cache.c`.
- Memory buffer-based allocator.
- Entropy
- In the X.509 module, `mbedtls_x509_crt_parse_path()` is thread-safe..
- CTR-DRBG and HMAC-DRBG.
- The SSL session tickets callbacks provided in *ssl_ticket.c*.
- The DTLS CLientHello cookie callbacks provided in *ssl_cookie.c*.

This covers the most common cases in which you need to share a context across threads. If you have use cases in which you need to share another context across threads, please let us know.
