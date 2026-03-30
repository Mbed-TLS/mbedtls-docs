# Buffer underflow in `x509_inet_pton_ipv6()` (CVE-2026-25833)

**Title** | Buffer underflow in `x509_inet_pton_ipv6()`
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-25833
**Date** | 31 March 2026
**Affects** | All versions of Mbed TLS from 3.5.0 up to 3.6.5 and 4.0.0
**Not affected** | Mbed TLS 3.6.6 and later 3.6 versions, 4.1.0 and later 4.x versions
**Impact** | Buffer underread
**Severity** | LOW
**Credits** | Haruto Kimura (Stella)

## Vulnerability

In cases where the platform/toolchain does not provide `inet_pton()` the library provides its own implementation. The library uses the macro `AF_INET6` as a heuristic and provides its own implementation whenever this macro is not defined.

If the library provided implementation is used, there is a buffer underflow in `x509_inet_pton_ipv6()`. When the function detects IPv4 mapped parts, it walks back to the start of the start of it and calls another function to parse it. There is a flaw in the logic and this part can walk back before the start of the buffer, causing a buffer underread of at most 4 bytes.

## Impact

The buffer underread on some platforms (e.g. on platforms with memory protection when the overread crosses page boundary), in rare cases could lead to DoS.

## Affected versions

All versions of Mbed TLS from 3.5.0 up to 3.6.5 and 4.0.0 are affected.

## Work-around

Use a toolchain that provides `inet_pton()` and defines the `AF_INET6` macro.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.6 or 4.1.0

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.x | Mbed TLS 4.x |
| ------ | -------------- | ----------------- | ------------ |
| Basic fix | 4595bb47d27c2aae522c54eca28605f270ab5f5a | N/A | 1a127e3c892076dd9725fce2ee10015eb20448f4 |
| With tests and documentation | branch up to 72e18e003297c6f06dd87b207b332b710a6ce20a | N/A | branch up to 50376926a7356c25da12f1d2e66cacf2d3e9bbcb |
