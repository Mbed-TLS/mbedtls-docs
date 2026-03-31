# Entropy on Linux can fall back to /dev/urandom (CVE-2026-34871)

**Title** | Entropy on Linux can fall back to `/dev/urandom`
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-34871
**Date** | 31 March 2026
**Affects** | All versions of Mbed TLS up to 3.6.5; all versions of TF-PSA-Crypto up to 1.0.0
**Not affected** | Mbed TLS 3.6.6 and later 3.6 versions; TF-PSA-Crypto 1.1.0 and later versions
**Impact** | Lack of randomness on newly initialized Linux device without a hardware random generator
**Severity** | LOW
**Credits** | supers1ngular (BayLibre)

## Vulnerability

Mbed TLS and TF-PSA-Crypto rely on the operating system or hardware to obtain entropy to seed its random generator. On Linux, the library uses the `getrandom()` system call if available, and falls back to reading from a special device otherwise. Historically, the special device was hard-coded to be `/dev/urandom`.

Using `/dev/urandom` for cryptography on Linux is fine except in one specific scenario: if the device has recently booted and has not had time to accumulate enough entropy yet, `/dev/urandom` may return predictable data. This is especially a concern on embedded devices without any peripherals that have significant entropy.

Many Linux distributions arrange to save entropy across reboots, in which case `/dev/urandom` is safe after that entropy file has been loaded. However, `/dev/urandom` can be unsafe early during the boot phase, or while (re)installing the operating system.

The library does try to use `getrandom()`, which will wait for enough entropy to be available. However there are several scenarios where `/dev/urandom` is used:

* On Linux kernels older than 3.17, the `getrandom()` system call does not exist, and the library will fall back to `/dev/urandom`.
* The program may run in a confined environment that blocks access to the `getrandom()` system call, and the library will fall back to `/dev/urandom` at run time.
* Depending on the C library, the library code may not be able to find the system call. Mbed TLS and TF-PSA-Crypto can use `getrandom()` if built with headers from non-ancient versions of GNU libc or uCLibc. Otherwise it will only use `/dev/urandom`.

## Impact

On Linux, if `/dev/urandom` is used at a time when the system does not have enough entropy, then all cryptographic operations that rely on randomness may be compromised. All keys generated during this time are potentially predictable. Also, if randomized ECDSA signatures are generated during this time, this may compromise the signature key. (RSA, and deterministic ECDSA, are safe in this respect: the signature process cannot leak the key. The library will use deterministic ECDSA if available at build time unless the randomized variant is explicitly requested.)

This is especially a concern when installing an operating system on a device that lacks a hardware random generator.

## Affected versions

All versions of Mbed TLS up to 3.6.5 are affected. TF-PSA-Crypto 1.0.0 and Mbed TLS 4.0.0 are also affected. Only Linux platforms are affected.

## Work-around

Applications using an affected version of the library on Linux should ensure that either the library uses `getrandom()`, or the Linux kernel has enough entropy before using TF-PSA-Crypto or Mbed TLS for anything that requires randomness.

* Devices that have a dedicated hardware random generator (“true RNG”) used by the Linux kernel are safe.
* Builds using Glibc or uClibc, running on a kernel where `getrandom()` is available, are safe.
* Builds using a custom entropy callback (`MBEDTLS_ENTROPY_HARDWARE_ALT` or `MBEDTLS_PSA_DRIVER_GET_ENTROPY`) are safe (assuming the entropy callback doesn't rely on `/dev/urandom` unsafely).
* Applications that don't run during the device installation or during the early boot phase are safe, provided that the Linux distribution arranges for an entropy file to be loaded during the system boot.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.6 or a later 3.6.x version, or to TF-PSA-Crypto 1.1.0 or above.

In these versions, the library uses `/dev/random` if `getrandom()` is not available, which is safe but may block on Linux kernels older than 5.6 even when enough entropy is available. Package maintainers may move back to using `/dev/urandom` by setting the new configuration option `MBEDTLS_PLATFORM_DEV_RANDOM`. Applications may set the new global variable `mbedtls_platform_dev_random` to override the compile-time default.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.x | Mbed TLS 4.x |
| ------ | -------------- | ----------------- | ------------ |
| Minimal fix | replace `/dev/urandom` by `/dev/random` in `library/entropy_poll.c` | replace `/dev/urandom` by `/dev/random` in `drivers/builtin/src/platform_util.c` | N/A |
| With configurability | branch up to 03fafd2637a4d7180ce3fe6cbb436858f2cbfd53 | branch up to 6ce2975d3406703f724293686d7dc49b4dc8d80b | N/A |
