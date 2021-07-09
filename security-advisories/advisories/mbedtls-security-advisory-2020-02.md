# Cache attack against RSA key import in SGX

**Title** |  Cache attack against RSA key import in SGX
---|---
**Date** |  20th February 2020
**Affects** |  All versions of Mbed TLS and Mbed Crypto
**Impact** |  The RSA private key is recoverable through side channels.
**Severity** |  Medium
**Credit** |  Alejandro Cabrera Aldaya and Billy Brumley

## Vulnerability

If Mbed TLS is running in an SGX enclave and the adversary has control of the
main operating system, they can launch a side channel attack to recover the
RSA private key when it is being imported. Found by Alejandro Cabrera Aldaya
and Billy Brumley and reported by Jack Lloyd.

The attack only requires access to fine grained measurements to cache usage.
Therefore the attack might be applicable to a scenario where Mbed TLS is
running in TrustZone secure world and the attacker controls the normal world
or possibly when Mbed TLS is part of a hypervisor and the adversary has full
control of a guest OS.

## Impact

If an adversary has fine grained measurements to cache usage at the time an
RSA key is being imported, they are able to recover the private key.

## Resolution

Affected users should upgrade to one of the most recent versions of Mbed TLS,
including 2.21.0, 2.16.5 or 2.7.14 or later. Similarly, affected users should
upgrade to the most recent version of Mbed Crypto, including 3.1.0 or later.

**Warning:** Even in these versions, it is only safe to import complete RSA
private keys. `mbedtls_pk_parse_key()` and `mbedtls_pk_parse_keyfile()` can
only import complete private keys and therefore using them is safe. Use of
lower level APIs (such as `mbedtls_rsa_import()`) or direct access to the
members of the `mbedtls_rsa_context` structure for importing keys is only safe
if all the needed parameters are provided; in configurations with
`MBEDTLS_RSA_NO_CRT` undefined (which is the default), this means all the
components prescribed by appendix A.1.2 of the PKCS#1 v2.2 standard; in
configurations with `MBEDTLS_RSA_NO_CRT` enabled, this means n, e, d, p and q.

## Workaround

There are no known workarounds.

### Like this?

**Section:**
Security Advisories

**Author:**
Janos Follath

**Published:**
Feb 18, 2020

**Last updated:**
Feb 21, 2020