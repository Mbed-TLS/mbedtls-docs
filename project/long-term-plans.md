# Long-term plans for Mbed TLS

This page lists some ideas that are being considered for Mbed TLS. Just because something is listed on this page does not mean that it definitely will be done, but means that it is a consideration and might influence decisions about the evolution of related features. This page is intended to list ideas that have a significant influence on the design of the library as a whole and typically omits proposals that span a single module.

## Library organization

### Project split

There is a plan to split Mbed TLS into a PSA cryptography library and an X.509+TLS library. In the long term, the PSA cryptography library will only offer `psa_xxx` interfaces, and [the `mbedtls_xxx` cryptography interfaces will no longer exist](#making-psa-crypto-the-only-crypto-api). In the shorter term, we are planning an intermediate step where the PSA cryptography reference implementation is its own repository, but that repository still exposes legacy cryptography interfaces, and Mbed TLS will consume and re-expose both interfaces.

Experience with the ill-fated Mbed Crypto split has shown that before doing this, significant preparation is needed:

* Some parts of crypto are mostly only useful for X.509 or TLS. For example ASN.1, OID and possibly pk should probably be in X.509, with a few ad special hoc cases implemented independently in crypto.
* Many files need to be split because they have both crypto and non-crypto aspects: build scripts, test scripts, test support code, `error.c`, etc.

### Bignum redesign

The current bignum module relies heavily on the use of `malloc`. This requires dynamic allocation, is inefficient, and can leak the size of intermediate results which is a concern with some numerical algorithms. Most functions are not constant-time.

The module supports negative numbers, which are generally not relevant for cryptography and complicate many algorithms. Support for negative numbers is likely to be removed once the part of the ECC code that takes advantage of it is rewritten.

Since Mbed TLS 3.3.0, we are have started to redesign the bignum code. New internal library modules perform arithmetic on numbers modulo N, without any dynamic allocation. Asymmetric crypto modules will be rewritten to use these new arithmetic primitives. We will also gradually extend the set of functions that are constant-time.

### Replacing ALT implementations by PSA drivers

It is currently possible to replace some of the library modules and functions by alternative implementations by defining a symbol `MBEDTLS_xxx_ALT` and linking with a custom implementation of the corresponding functions. This is typically useful when the custom implementations calls cryptographic acceleration hardware.

The design of the ALT interfaces is cumbersome, especially when replacing a whole module. The ALT implementer must respect the semantics of the original functions, and cannot easily reuse part of the exiting code (for example, to perform padding). This limits the evolution possibilities of the library since changes of semantics that are backward-compatible for applications usually break ALT implementations.

In Mbed TLS 3.0, existing ALT implementations continue to work, since PSA drivers are not fully implemented yet. However, it is likely that no new ALT possibility will be added. Once PSA drivers are ready for production, ALT implementations will be deprecated, likely to be removed in Mbed TLS 4.0.

## API design

### Making PSA Crypto the only crypto API

Currently there are two APIs for most crypto operations:

- one in the `mbedtls_` namespace, which historically was the only one - referred to as "the legacy crypto API" below;
- one in the `psa_` namespace, which was added more recently (first experimental and now stable both in the development branch and the current LTS branch), which implements the Crypto part of the [PSA Certified API Specification](https://arm-software.github.io/psa-api/) - referred to as "the PSA Crypto API" below.

As it is undesirable to maintain two APIs in the long run, we are going to retire the legacy API in the future, leaving the PSA Crypto API as the only API for crypto operations. The timeline and details have not been decided yet, however it is likely that in the next major version (Mbed TLS 4.0), most (if not all) of the legacy API will be removed from our public API, with possible exceptions for the abstraction layers PK, Cipher and MD. The current options `MBEDTLS_PSA_CRYPTO_C`, `MBEDTLS_USE_PSA_CRYPTO` and `MBEDTLS_PSA_CRYPTO_CONFIG` will effectively be always enabled.

Note that the bignum/MPI API, though it's not a crypto API, will also likely be removed from our public API at this point. This follows the general trend of making more things opaque/private (for example, most struct members became private in Mbed TLS 3.0).

The X.509 and TLS APIs (`mbedtls_x509_` and `mbedtls_ssl_` namespaces) will of course remain, only the legacy crypto API is being retired. Some functions in those modules may change signature / argument types, but other than that those APIs are unaffected.

### Simplify and unify error codes

Currently, `mbedtls_xxx` functions return `MBEDTLS_ERR_xxx` error codes, and `psa_xxx` functions return `PSA_ERROR_xxx` error codes. These use overlapping value spaces, so a function has to pick, it's impossible for a function to return either kind of error code depending on the error.

We plan to renumber `MBEDTLS_ERR_xxx` error codes so that there is no overlap. Then we could have all functions return a `psa_status_t`, and we wouldn't need to convert between the two sets (which adds complexity and code size).

With this renumbering, `MBEDTLS_ERR_xxx` error codes that have a matching PSA error will be merged. There will no longer be separate error codes for similar errors in different modules. For example, all `MBEDTLS_ERR_xxx_ALLOC_FAILED` will be replaced by `PSA_ERROR_INSUFFICIENT_MEMORY`.

As part of this change, we also plan to remove the association of “low-level” and “high-level” Mbed TLS error codes. Error codes will work like an enum.

Merging error codes break legitimate code (`case ERR_FOO: case ERR_BAR:` is an error if `ERR_FOO` and `ERR_BAR` have the same value), so this change has to be done in a major release.

### Secure by default, hard to misuse

When designing new APIs, consideration should be given not only about the intended use case, but about how the API could be misused. A good API should mitigate the risks of vulnerabilities caused by its misuse.

Documentation helps. For example, the documentation should always be explicit about memory ownership, responsibility for validation, etc. Some of the existing documentation is not up to the standards we have for new documentation in this respect.

However, documentation alone is not sufficient. If an application developer does not read the documentation, we cannot guarantee that the application will be secure, but we do want to make it less likely to have severe vulnerabilities. It's worth it if as a consequence of the API design, it takes more work to get an application to pass its functional tests, but the result is more likely to be secure.

Any defaults should either be a secure parameter, or one that is rejected as invalid. This includes, for example, a field in a structure that was `memset` to 0 and not explicitly initialized: 0 or `NULL` should either be invalid or be something “safe”, it should not mean that a security countermeasure is turned off. (Beware that this principle is not always followed in existing APIs!)

### Reducing dynamic memory allocation

Getting rid of `malloc` is a frequent request. It is not uncommon for single-purpose applications running on dedicated devices to use a heap solely for the purpose of Mbed TLS (which is why the library offers the `memory_buffer_alloc` module). Some high-safety application domains forbid dynamic memory allocation altogether.

Getting rid of dynamic allocation inside the library is a difficult task involving extensive changes to the API. As the API evolves, we try to make it more friendly to malloc-less usage. For example, the move from `mbedtls_{cipher,md,pk}_xxx` to PSA APIs is a step in this direction: the PSA API was designed so that it can be reasonably implemented without dynamic allocation (even if the current Mbed TLS implementation does not always take advantage of this design yet).

## Features

### New cryptographic algorithms

The Mbed TLS maintainers are always open to adding new cryptographic mechanisms that are suitable for production. The limiting factor is the bandwidth available for coding and reviewing. Mbed TLS is not limited to cryptographic mechanisms validated by any particular standards body, nor, as the name might suggest, to mechanisms used in the TLS protocol.

## Security

### More constant-trace code

The Mbed TLS maintainers generally consider timing-related side channels (including the leverage of features such as caches, branch prediction, variable-time instructions and other microarchitectural details) to be potential threats. As a consequence, we tend to make more and more code have execution traces that are independent of the secret data. Some parts of the library are still vulnerable to timing-related side channels, but this is unlikely to be acceptable in new code.

### Implementation design

Here are a few general guidelines, which we try to propagate throughout the library even if they are not always followed by existing code.

* Secret data should not leak through output buffers on failure.
* Local variables and output parameters should be initialized to a safe default. For example, it is already current practice to initialize error code variables to `MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED` or `#PSA_ERROR_CORRUPTION_DETECTED`, and set them to `0` or `PSA_SUCCESS` only when a success condition has been detected.
* Memory blocks that may have contained sensitive data should be zeroized before their scope ends. This is already generally followed, and any omission in this regard will likely be considered a security bug.
