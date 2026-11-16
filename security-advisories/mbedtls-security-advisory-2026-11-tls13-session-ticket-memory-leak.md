# TLS 1.3 session ticket rejection resource leak (CVE-2026-115491)

**Title** | TLS 1.3 session ticket rejection resource leak
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-115491
**Date** | 16 November 2026
**Affects** | Mbed TLS 3.6.0 through 3.6.7; Mbed TLS 4.0.0-beta through 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 3.5.2 and earlier; Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later
**Impact** | Repeated rejected TLS 1.3 session tickets may exhaust memory and prevent new TLS operations
**CWE** | CWE-401: Missing Release of Memory after Effective Lifetime
**CAPEC** | CAPEC-272: Protocol Manipulation; CAPEC-131: Resource Leak Exposure
**Severity** | LOW
**Credits** | Duong Gia Huy

## Vulnerability

When an Mbed TLS server processes the pre-shared-key extension in a TLS 1.3
ClientHello, it asks the configured ticket parser to load each matching ticket
into a temporary session. If Mbed TLS later determines that no recorded PSK key
exchange mode is usable, it rejects the ticket and continues processing without
freeing resources owned by the temporary session. This leaves heap-backed
session data allocated after the failed resumption attempt.

With the standard Mbed TLS ticket parser, the heap memory allocated to store
the ALPN value from a TLS 1.3 ticket is not freed when both `MBEDTLS_SSL_EARLY_DATA`
and `MBEDTLS_SSL_ALPN` are enabled at build time. This allocation is made even
if the server does not enable early data at run time with
`mbedtls_ssl_conf_early_data()`. An application-provided ticket parse callback
can leak heap memory allocated for other session data. A remote peer with a
still-valid ticket can reach this path, and can repeat an identity in one
ClientHello to leak one allocation per identity.

## Impact

Repeated ticket rejections can permanently consume memory, reducing the
server's ability to process later TLS operations. This can eventually cause
allocation failures, failed TLS handshakes, or a server crash.

## Affected versions

All versions of Mbed TLS from 3.6.0 to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0-beta to 4.1.1 are affected.
Mbed TLS 4.2.0 is affected.

## Work-around

If an upgrade is not possible, disable session tickets completely by building
without `MBEDTLS_SSL_SESSION_TICKETS` or by removing the configured ticket
callbacks. This disables both TLS 1.2 and TLS 1.3 session tickets.

Applications using the standard ticket parser can also avoid the leaked
allocation by not negotiating ALPN, or by building without either
`MBEDTLS_SSL_EARLY_DATA` or `MBEDTLS_SSL_ALPN`; disabling either build-time
option is sufficient.

If ticket acceptance remains enabled, previously issued affected tickets must
also be invalidated.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version, Mbed
TLS 4.1.2 or a later 4.1.x version, or Mbed TLS 4.3.0 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | -------------------- |
| Basic fix | d58c1f7287d21342fa448ba2f816559579abc3fd^..0cabe922c1bd9913e8001a02df7c2144aefdc61c | 1848d119114da9c34f33eebe3d8e3d3934a7e898^..aaff2c3d5a89a1748089147d5aaa730b65fe2a85 | a5efa52696272780f1529ee45d6ebabd99b33d64^..d193abb7a63f5de030b178c0adda504d177c53ea |
| With tests and documentation | d4caa51f3f9dce7f4e9ea3b15ca72432fd3bf7e6^..aa36393f140341b4a47ba67a9344b26d04a1ab93 | a8c07c4b90a57148d4983a906c79eb190a943d7f^..a248317112f147ebac571d1eec4f1a7716df3860 | d4058840475fcb53c1f7b6988b310ea949fd54d7^..9f03c3a1641dff3d216b176808e2b66cb31267c7 |
