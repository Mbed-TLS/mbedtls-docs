# The external dependencies Mbed TLS relies on

## External function dependencies

Mbed TLS is as loosely coupled as possible and does not rely on any external libraries for its code. It does use a number of standard `libc` function calls. This page describes which external calls are present and how you can remove them if no support for that function is available; it focuses on the core library only (excluding the example programs and test suites, but including the self test functions as they are part of the library).

Configuration flags control some of the dependencies. Please see [How do I configure mbed TLS](../compiling-and-building/how-do-i-configure-mbedtls.md) and [How do I port Mbed TLS to a new environment or OS](../how-to/how-do-i-port-mbed-tls-to-a-new-environment-OS.md) for a full description of how to set the configuration flags to port Mbed TLS to a new environment.

## Signals and alarms

Both `net_sockets.c` and `timing.c` use signal handlers. The `timing.c` file uses them as support code for example programs. The signal handlers in `net_sockets.c` serve a more direct purpose. You can remove this dependency by disabling or adapting the example programs and using alternate I/O callbacks instead of `net_sockets.c` in the TLS layer.

**Functions covered:** `signal()`

Only `timing.c` uses `alarm()`. This code is only used in example programs as support code, not in the actual library. You can remove this dependency.

**Functions covered:** `alarm()`

## Select

Only `net_sockets.c` uses `select()`, for the purposes of sleeping (only used in the example programs, not in the library) or providing blocking reads with timeouts. You can remove this dependency by using alternate I/O callbacks instead of `net_sockets.c` in the TLS layer.

**Functions covered:** `select()`

## Network/socket based functions

The network and socket based functions are only used in the *Network* module (`net_sockets.c`). As the TLS part only uses function pointers, you can replace these dependencies with something else (such as lwIP) as long as the behavior is similar. To use different networking functions, disable `MBEDTLS_NET_C`, and implement your own socket module, as described in [the porting article](../how-to/how-do-i-port-mbed-tls-to-a-new-environment-OS.md).

**Functions covered:** on Windows, functions from the Windows Sockets API, and on Unix:

- `accept()`
- `bind()`
- `close()`
- `connect()`
- `fcntl()`
- `freeaddrinfo()`
- `getaddrinfo()`
- `getsockname()`
- `getsockopt()`
- `listen()`
- `read()`
- `recvfrom()`
- `setsockopt()`
- `shutdown()`
- `socket()`
- `write()`

## Time related functions

The *Timing* module (`timing.c`) uses `gettimeofday()` to determine the elapsed time with a millisecond resolution. This is optionally used in the TLS layer for DTLS retransmission timers through callbacks. You can avoid this dependency by providing your own implementation of these callbacks to the TLS layer, with the definition of `MBEDTLS_TIMING_ALT`.

The *Timing* module may also use `gettimeofday()` if it doesn't know how to access the CPU cycle counter on your platform, or if `MBEDTLS_HAVE_ASM` is disabled. This is used in the example programs (currently only `benchmark.c`) as a support function, as a weak entropy source, and as a weak `RNG` algorithm (`havege`). You can remove this dependency by using stronger `RNG` algorithms and stronger entropy sources.

**Functions covered:** `gettimeofday()`

The `time()` function is abstracted as `mbedtls_time()`, in case `MBEDTLS_HAVE_TIME` is defined, and no alternative implementation was given with the definition of `MBEDTLS_PLATFORM_TIME_ALT` or no `MBEDTLS_PLATFORM_TIME_MACRO` was set. The `mbedtls_timetime()` function will be used by the *TLS core* modules, as well as the provided implementation of the following callbacks: SSL session cache, SSL session tickets, DTLS hello cookies. All these modules only rely on time differences. In other words, they do not need `time()` to return the correct time, much less the correct date. You can remove this dependency by disabling `MBEDTLS_HAVE_TIME` in the `mbedtls_config.h` file, but you may loose some features, such as time-based rotation of session ticket keys. Alternatively, you can supply a different implementation for `mbedtls_time()`, by defining `MBEDTLS_PLATFORM_TIME_ALT()` and call `mbedtls_platform_set_time()` to set your own time function.

If your platform supports a time function, with a different name, but same functionality, you can set it as `MBEDTLS_PLATFORM_TIME_MACRO` (with a possibility of defining `MBEDTLS_PLATFORM_TIME_TYPE_MACRO` as well).

**Functions covered:** `time()` (relative)

If `MBEDTLS_HAVE_TIME_DATE` is defined, `mbedtls_time()` and `mbedtls_platform_gmtime_r()` are used by `x509.c` to check if a certificate has expired. `mbedtls_platform_gmtime_r` is an abstraction layer for the thread safe version of `gmtime()`, which is automatically configured by the library according to the underlying system, or falling back to `gmtime()` if not supported by the system, protected by a mutex `mbedtls_threading_gmtime_mutex`. Note that this mutex should be shared across the entire system, in order for the `gmtime()` to be truly thread safe. Alternatively, you can implement your own thread safe version of `mbedtls_platform_gmtime_r()` with the definition of `MBEDTLS_PLATFORM_GMTIME_R_ALT`.
You can remove this dependency by disabling `MBEDTLS_HAVE_TIME_DATE`, but then the date-based certificate expiration will not be used (revocation through CRLs, for example, will still work).

**Functions covered:** 

- `time()` (absolute)
- `gmtime()`, `gmtime_r()` or `gmtime_s()` (depending on the system)

## File (stream) functions

If `MBEDTLS_FS_IO` is defined, the file functions are used in several Mbed TLS modules:

- The MD layer for file hashing (`mbedtls_md_file()`).
- *X509 Parsing* (`x509_crt.c`, `x509_crl.c`, `x509_csr.c`) use the file functions for reading the certificate, CSR and CRL files; it also uses `readdir()` for `mbedtls_x509_crt_parse_path()`.
- The PK layer (`pkparse.c`) uses file functions for reading and parsing keys from files.
- The *MPI* module (`bignum.c`) uses `fwrite` for writing MPIs to files and streams and `fgets` for reading files and streams into MPIs.
- The entropy, *CTR-DRBG* and *HMAC_DRBG* modules use file functions for reading and updating seed files.
- The *DHM* module uses file operations to read DH parameters files (`mbedtls_dhm_parse_dhmfile`).

You can disable all by commenting `MBEDTLS_FS_IO` in `mbedtls_config.h`.

**Functions covered:** 

- `fclose()`
- `ferror()`
- `fgets()`
- `fopen()`
- `fread()`
- `fseek()`
- `ftell()`
- `fwrite()`
- `readdir()`
- `closedir()`


## Dynamic memory functions

A number of modules (ASN1, Bignum/MPI, Cipher, CMAC, DHM, ECP, MD, PEM, PK, PKCS11, RSA, TLS, X.509) use dynamic memory allocation. You can provide your own implementations, and we even provide a buffer-based memory allocator. For further details, read [Letting Mbed TLS use static memory instead of the heap](../how-to/using-static-memory-instead-of-the-heap.md).

**Functions covered:** 

- `free()`
- `calloc()`

## Memory functions

The functions `memcmp()`, `memcpy()` and `memset()` are really basic in any system and used in several places. The assumption is that everybody has support for these.

**Functions covered:** 

- `memcmp()`
- `memcpy()`
- `memset()`

The `memmove()` function is used as an optimization in the *TLS* module. It is also used in the nist key wrapping module (`nist_kw.c`) and in the NULL cipher wrap (`null_crypt_stream`) to avoid buffer overlapping. You can remove this dependency by providing your own implementation of the same functionality.

**Functions covered:** `memmove()`

## String functions

The `printf()` function is used in all self test functions as `mbedtls_printf()`, controlled by the `MBEDTLS_SELF_TEST` configuration flags. In addition, in the *MPI* module (`bignum.c`), `mbedtls_mpi_write_file()` uses `mbedtls_printf()` to print to `stdout` if `MBEDTLS_FS_IO` is defined. You can disable these dependencies in the `mbedtls_config.h` file. You can also provide your own implementation through the platform layer, see `MBEDTLS_PLATFORM_PRINTF_ALT` for an example. If your platform supports a print function with a different name, you can set it as `MBEDTLS_PLATFORM_PRINTF_MACRO`.

**Functions covered:** `printf()`

The `snprintf()` function is defined as `mbedtls_snprintf()`. It is used in the *X.509* module for the various `mbedtls_x509_xxx_info()` functions and `mbedtls_x509_crt_parse_path()`. It is also used by the *SSL debug* module (`debug.c`) for formatting debug messages, by `error.c` for `mbedtls_strerror()` and by `oid.c` for `mbedtls_oid_get_numeric_string()` (not used in the library). You can provide your own implementation through the platform layer, see `MBEDTLS_PLATFORM_PRINTF_ALT` for an example. If your platform supports a similar function with a different name, you can set it as `MBEDTLS_PLATFORM_SNPRINTF_MACRO`.

**Functions covered:** `snprintf()`

The other string functions are used in actual core scenarios. There are workarounds possible in any of there scenarios.

**Functions covered:** 

- `strcmp()`
- `strlen()`
- `strncmp()`
- `strncpy()`
- `strstr()`

## Random function

The `rand()` function is used only in the self tests of the RSA module (`rsa.c`). You can disable it by `MBEDTLS_SELF_TEST`.

**Functions covered:** `rand()`

## Variable argument functions

To make a half-compatible `snprintf()` function under Windows, you can use `va_start()`, `va_end()`, and `vsnprintf()`. All three are also used in the *Debug* module (`debug.c`). You can remove `vsnprintf()` by commenting `MBEDTLS_DEBUG_C`. 

**Functions covered:** 

- `va_start()`
- `va_end()`
- `vsnprintf()`
