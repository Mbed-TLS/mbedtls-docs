# TLS 1.3 transform setup resource leak (CVE-2026-93843)

**Title** | TLS 1.3 transform setup resource leak
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-93843
**Date** | 16 November 2026
**Affects** | Mbed TLS 3.1.0 through 3.6.7; Mbed TLS 4.0.0 through 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 2.28.10 and earlier; Mbed TLS 3.0.x; Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later 4.x versions
**Impact** | Repeated failed TLS 1.3 handshakes may exhaust memory or PSA key slots and prevent new TLS operations
**CWE** | CWE-772: Missing Release of Resource after Effective Lifetime; CWE-401: Missing Release of Memory after Effective Lifetime
**CAPEC** | CAPEC-131: Resource Leak Exposure
**Severity** | LOW
**Credits** | Xiangdong Li

## Vulnerability

When Mbed TLS sets up a TLS 1.3 transform, it creates cipher contexts in builds that do not use PSA crypto, or imports traffic keys into PSA in PSA-backed builds. If a later setup step fails after an earlier resource has been acquired, the transform setup returns an error. Its callers free the transform allocation without releasing resources owned by the transform. This can leave cipher contexts or PSA key slots allocated after the failed connection setup.

The failure requires a local allocation or cryptographic-backend error after an earlier resource acquisition. In Mbed TLS 3.6, this affects both PSA and non-PSA builds. Mbed TLS 4.x uses the PSA-backed transform path. A remote peer can initiate TLS 1.3 handshakes that reach this code path.

## Impact

Repeated failures can consume memory or PSA key slots, reducing the server's ability to process later TLS operations.

## Affected versions

TLS 1.3-enabled applications using Mbed TLS 3.1.0 through 3.6.7, 4.0.0 through 4.1.1, or 4.2.0 are affected. In Mbed TLS 3.6, this affects both PSA and non-PSA builds. Applications that do not build TLS 1.3 are not affected.

## Work-around

If an upgrade is not possible, disable TLS 1.3 for the affected configuration by setting its maximum TLS version to TLS 1.2 with `mbedtls_ssl_conf_max_tls_version(conf, MBEDTLS_SSL_VERSION_TLS1_2)`. Alternatively, disable TLS 1.3 at build time by building without `MBEDTLS_SSL_PROTO_TLS1_3`.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version, Mbed TLS 4.1.2 or a later 4.1.x version, or Mbed TLS 4.3.0 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | -------------------- |
| Basic fix | 3626aa2d3482204105bc760b4b80e91ba6efb756 afa648aa44c698f6f01b1dd653edc3dfbe140355 | 14b15fcabfa19ea1930f579115c704041e772068 | 113010a9d674ccfd28f9c1409aa5e0d80c0beea1 |
| With tests and documentation | 27e5c190dc753c0d493254bab11d0b22de1774f6..afa648aa44c698f6f01b1dd653edc3dfbe140355 | 0970a715f11559a5ad0969a78ceb51a9fc78dcb1..433c88651aebe12e85eafcc310cdd13a9373a097 | de23569aa95ac518e1c794236219dcb04fca4ae5..e0766f1b4a2133ea043e10cef86cc1c76f69b49b |
