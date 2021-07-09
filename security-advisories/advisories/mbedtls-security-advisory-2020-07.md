# Side-channel attack on ECC key import and validation

**Title** |  Side-channel attack on ECC key import and validation
---|---
**Date** |  1st of July, 2020
**Affects** |  All versions of Mbed TLS and Mbed Crypto
**Impact** |  A local attacker can extract the private key
**Severity** |  High
**Credit** |  Alejandro Cabrera Aldaya and Billy Brumley

## Vulnerability

The scalar multiplication function in Mbed TLS accepts a random number
generator (RNG) as an optional argument and, if provided, uses it to protect
against some attacks, including a [previous attack](https://tls.mbed.org/tech-
updates/security-advisories/mbedtls-security-advisory-2020-04) by the same
authors.

It is the caller's responsibility to provide a RNG if protection against side-
channel attacks is desired; however two groups of functions in Mbed TLS itself
fail to pass a RNG:

  1. `mbedtls_pk_parse_key()` and `mbedtls_pk_parse_keyfile()`
  2. `mbedtls_ecp_check_pub_priv()` and `mbedtls_pk_check_pair()`

When those functions are called, scalar multiplication is computed without
randomisation, a number of old and new attacks apply, allowing a powerful
local attacker to fully recover the private key.

It should be noted that the first group of function only performs a scalar
multiplication if the private key being parsed doesn't include the public key,
or includes the public key in compressed formats. Common tools for generating
key pairs tend to include the public key in uncompressed format in the encoded
private key; in that case parsing functions were safe from this attack.

## Impact

An attacker with access to precise enough timing and memory access information
(typically an untrusted operating system attacking a secure enclave such as
SGX or the TrustZone secure world) can fully recover the private key after
collecting a single trace of any of the affected functions.

## Resolution

Affected users will want to upgrade to Mbed TLS 2.23.0, 2.16.7 or 2.7.16
depending on the branch they're currently using.

## Workarounds

For the parsing functions, making sure all keys being parsed always include
the uncompressed public key avoids the vulnerability.

For the pair-checking functions, there is no work-around except refraining
from using them (they're never called from any other library function).

If your application calls `mbedtls_ecp_mul()` or
`mbedtls_ecp_mul_restartable()` directly, you want to make sure that you're
always passing a non-NULL `f_rng` parameter, pointing to a well-seeded
instance of a secure RNG.

### Like this?

**Section:**
Security Advisories

**Author:**
Manuel Pégourié-Gonnard

**Published:**
Jun 30, 2020

**Last updated:**
Jul 1, 2020