# TLS 1.2 renegotiation can disclose memory during output buffer resize (CVE-2026-115488)

**Title** | TLS 1.2 renegotiation can disclose memory during output buffer resize
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-115488
**Date** | 16 November 2026
**Affects** | Mbed TLS 2.22.0 through 3.6.7; Mbed TLS 4.0.0 through 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 1.3.10 through 2.20.0; Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later 4.x versions
**Impact** | A TLS peer may receive memory from the server process, and the affected TLS connection may fail.
**CWE** | CWE-125: Out-of-bounds Read
**CAPEC** | CAPEC-123: Buffer Manipulation
**Severity** | HIGH

## Vulnerability

When variable-length TLS buffers are enabled, Mbed TLS can shrink its buffers after negotiating a smaller Maximum Fragment Length (MFL), then grow them when TLS 1.2 renegotiation starts. If a server has only partly sent an application record when it processes a peer's renegotiation request, resizing resets the output header pointer but retains the count of pending bytes. The next flush can therefore pass a pointer before the output buffer to the network send callback, exposing adjacent process memory to the peer.

The affected path requires `MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH`, `MBEDTLS_SSL_MAX_FRAGMENT_LENGTH` with a smaller fragment negotiated, and `MBEDTLS_SSL_PROTO_TLS1_2`; the server must also accept renegotiation (enabled by `MBEDTLS_SSL_RENEGOTIATION`) and have pending output when it processes the renegotiation.

## Impact

A connected TLS peer may receive adjacent heap contents from the server process. The corrupted record can also cause the connection to fail.

## Affected versions

Mbed TLS 2.22.0 through 3.6.7, Mbed TLS 4.0.0 through 4.1.1, and Mbed TLS 4.2.0 are affected.

## Work-around

Until upgrading, disable `MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH` at build time, or disable TLS 1.2 renegotiation at runtime by calling `mbedtls_ssl_conf_renegotiation(conf, MBEDTLS_SSL_RENEGOTIATION_DISABLED)` when configuring the server. Renegotiation is disabled by default at runtime.

## Resolution

The issue is fixed in Mbed TLS 3.6.8, 4.1.2, and 4.3.0. Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version, Mbed TLS 4.1.2 or a later 4.1.x version, or Mbed TLS 4.3.0 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x>1) |
| ------ | -------------- | -------------- | ------------------- |
| Basic fix | 574e868886140558d89a8bd7047af17ec166129e | 194fe6c615d5702dd13b6bd69737007480cd1cd0 | 4f155913fa717a3bb32945a38128f88be34426c2 |
| With tests and documentation | 9082e54bdcaacf5f458582725185411d7b113c88..a32fbc5c914f439ab41b50e540349d65e6af9b2a | 3ef8776b72eecda298907ce9f82892ffc0c99ed7..15dd8747636b13397c15629b5676fe3e8931faec | 4a4de5b8fb7221e22869b5acf75e5c49c4a0a929..34e78cd97d9208dde66f5f31070b76e0db857ed0 |
