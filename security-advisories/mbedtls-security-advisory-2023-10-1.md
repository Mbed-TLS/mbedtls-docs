# Buffer overread in TLS stream cipher suites

**Title** |  Buffer overread in TLS stream cipher suites
---|---
**CVE** |  CVE-2023-43615
**Date** |  05 October 2023
**Affects** |  All versions of Mbed TLS
**Impact** |  A remote attacker may cause a crash or information disclosure.
**Severity** |  Medium
**Credit** |  OSS-Fuzz

## Vulnerability

A peer in a (D)TLS connection using a null-cipher or RC4 cipher suite can send a malformed encrypted (or null-encrypted) record that causes a buffer overread of the vulnerable application. When the TLS parsing code calculates the MAC of the record, it subtracts the MAC length from the record length without checking if the record is large enough. As a consequence, if the payload of the record is shorter than the MAC, the code attempts to read slightly less than `SIZE_MAX` bytes to calculate the MAC of the received record.

Note that only weak cipher suites are affected: cipher suites using the null cipher (`TLS_xxx_WITH_NULL_hhh`, with authentication but not encryption) or RC4 (`TLS_xxx_WITH_RC4_128_hhh`, a weak and deprecated cipher, no longer supported after Mbed TLS 3.0). Those cipher suites are disabled in the default build-time configuration.

All protocol versions up to 1.2 are affected, including DTLS. TLS 1.3 is not affected. CBC and AEAD cipher suites are not affected.

## Impact

A (D)TLS peer that has successfully completed a handshake using a null-cipher or RC4 cipher suite can cause a buffer overread. On many platforms, this will result in a memory access fault. On platforms without memory protection, if the address space contains memory-mapped peripherals, the read operations can cause unpredictable results.

## Resolution

Affected users will want to upgrade to Mbed TLS 3.5.0 or 2.28.5 depending on the branch they're currently using.

## Work-around

The vulnerability is not present in the default build of Mbed TLS. It is only present if the compile-time configuration enables the vulnerable cipher suites. If you use a custom configuration and you want to check that the vulnerable cipher suites are not included in your build:

* In Mbed TLS 3.x or 2.28, make sure that `MBEDTLS_CIPHER_NULL_CIPHER` is not enabled.
* In Mbed TLS 2.28, also make sure that `MBEDTLS_REMOVE_ARC4_CIPHERSUITES` is enabled, or that `MBEDTLS_ARC4_C` is not enabled.

If the vulnerable cipher suites are enabled at compile time, they can be disabled at run time by calling `mbedtls_ssl_conf_ciphersuites()` with a list that does not include null-cipher or RC4 cipher suites. Alternatively, call `mbedtls_ssl_conf_ciphersuites_for_version()` for all affected protocol versions (SSLv3, TLS 1.0, TLS 1.1, TLS 1.2).

Applications that only accept TLS 1.3 are not affected.

The vulnerability only affects data records after a successful handshake, so if your TLS endpoint requires authentication, it can only be exploited by an authenticated client. Also, a firewall that prevents the negotiation of null-cipher or RC4 cipher suites will prevent the vulnerability from being exploited by traffic that goes through the firewall.
