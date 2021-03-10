# Long-term plans for Mbed TLS

This page lists some ideas that are being considered for Mbed TLS. Just because something is listed on this page does not mean that it definitely will be done, but means that it is a consideration and might influence decisions about the evolution of related features. This page is intended to list ideas that have a significant influence on the design of the library as a whole and typically omits proposals that span a single module.

## Library organization

### Project split

There is a plan to split Mbed TLS into a cryptography library and an X.509+TLS library. The split would be roughly between what currently gets built as `libmbedcrypto.a` and what gets built as `libmbedx509.a` + `libmbedtls.a`.

Experience with the ill-fated Mbed Crypto split has shown that before doing this, significant preparation is needed:

* Some parts of crypto are mostly only useful for X.509 or TLS. For example ASN.1, OID and possibly pk should probably be in X.509, with a few ad special hoc cases implemented independently in crypto.
* Many files need to be split because they have both crypto and non-crypto aspects: build scripts, test scripts, test support code, `error.c`, etc.

### Bignum redesign

The current bignum module relies heavily on the use of `malloc`. This requires dynamic allocation, is inefficient, and can leak the size of intermediate results which is a concern with some numerical algorithms. Most functions are not constant-time.

The module supports negative numbers, which are generally not relevant for cryptography and complicate many algorithms. Support for negative numbers is likely to be removed once the part of the ECC code that takes advantage of it is rewritten.

We would like to replace it with a module that performs constant-time arithmetic on numbers modulo N, without any dynamic allocation. As this requires an extensive change of the API of the bignum module, this is a major endeavor involving significant changes to asymmetric crypto modules.

### Replacing ALT implementations by PSA drivers

It is currently possible to replace some of the library modules and functions by alternative implementations by defining a symbol `MBEDTLS_xxx_ALT` and linking with a custom implementation of the corresponding functions. This is typically useful when the custom implementations calls cryptographic acceleration hardware.

The design of the ALT interfaces is cumbersome, especially when replacing a whole module. The ALT implementer must respect the semantics of the original functions, and cannot easily reuse part of the exiting code (for example, to perform padding). This limits the evolution possibilities of the library since changes of semantics that are backward-compatible for applications usually break ALT implementations.

In Mbed TLS 3.0, existing ALT implementations continue to work, since PSA drivers are not fully implemented yet. However, it is likely that no new ALT possibility will be added. Once PSA drivers are ready for production, ALT implementations will be deprecated, likely to be removed in Mbed TLS 4.0.

## API design

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
