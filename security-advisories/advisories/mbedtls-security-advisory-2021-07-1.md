# Local side channel attack on RSA

**Title** |  Local side channel attack on RSA
---|---
**CVE** |  (none)
**Date** |  7th of July, 2021
**Affects** |  All versions of Mbed TLS
**Impact** |  A powerful local attacker can extract the private key
**Severity** |  High
**Credit** |  Zili Kou, Wenjian He, Sharad Sinha, and Wei Zhang

## Vulnerability

The modular exponentiation operation in RSA uses a sliding window algorithm,
with a memory access pattern that depends on the bits of the secret key.

Exponent blinding is used as a counter-measure: it prevents an attacker from
correlating informations gathered on successive operation, but researchers
found a way to recover enough information by observing a single operation,
therefore by-passing this counter-measure.

## Impact

An attacker with access to precise enough timing and memory access information
(typically an untrusted operating system attacking a secure enclave such as
SGX or the TrustZone secure world) can recover the private keys used in RSA.

## Resolution

Affected users will want to upgrade to Mbed TLS 3.0.0, 2.27.0 or 2.16.11
depending on the branch they're currently using.

## Work-around

None.

### Like this?

**Section:**
Security Advisories

**Author:**
Manuel Pégourié-Gonnard

**Published:**
Jul 5, 2021

**Last updated:**
Jul 7, 2021