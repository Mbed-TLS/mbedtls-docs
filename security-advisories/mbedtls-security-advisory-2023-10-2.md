# Buffer overflow in TLS handshake parsing with ECDH

**Title** |  Buffer overflow in TLS handshake parsing with ECDH
---|---
**CVE** |  CVE-2023-45199
**Date** |  05 October 2023
**Affects** |  Mbed TLS 3.2.0 and above
**Impact** |  A remote attacker may cause arbitrary code execution.
**Severity** |  HIGH
**Credit** |  OSS-Fuzz

## Vulnerability

A TLS 1.3 client or server configured with support for signature-based authentication (i.e. any non-PSK key exchange) is vulnerable to a heap buffer overflow. An unauthenticated malicious peer can overflow the TLS handshake structure by sending an overly long ECDH or FFDH public key.

A TLS 1.2 server configured with `MBEDTLS_USE_PSA_CRYPTO` and with support for a cipher suite using ECDH and a signature is vulnerable to a heap buffer overflow. An unauthenticated malicious peer can overflow the TLS handshake structure by sending an overly long ECDH public key. TLS 1.2 clients, and builds with `MBEDTLS_USE_PSA_CRYPTO` are not affected.

## Impact

A malicious peer can overflow a buffer on the heap with attacker-controlled data. This can often be escalated to remote code execution.

## Resolution

Affected users will want to upgrade to Mbed TLS 3.5.0.

## Work-around

The default configuration is not affected. Mbed TLS 2.28 is not affected.
