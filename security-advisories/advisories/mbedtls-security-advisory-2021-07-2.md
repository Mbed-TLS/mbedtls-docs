# Local side channel attack on static Diffie-Hellman with Montgomery curves

**Title** |  Local side channel attack on static Diffie-Hellman with
Montgomery curves
---|---
**CVE** |  (none)
**Date** |  7th of July, 2021
**Affects** |  All versions of Mbed TLS and Mbed Crypto
**Impact** |  A local attacker can extract the private key
**Severity** |  High
**Credit** |  Leila Batina, Lukas Chmielewski, Björn Haase, Niels Samwel and
Peter Schwabe

## Vulnerability

The Montgomery curves Curve25519 and Curve448, also known as x25519 and x448
when used for Diffie-Hellman, were designed to minimize the number of checks
an implementation needs to do for secure use.

In particular, validity of the peer's public key needs not be checked, as long
as the underlying multi-precision (bignum) arithmetic is constant-time. This
is not the case in Mbed TLS, but validity checks were still skipped, so an
attacker could exploit special inputs (low-order points) in order to cause
variations in timing and memory access patterns that would in turn leak
information about the private key.

## Impact

An attacker with access to precise enough timing and memory access information
(for example, able to execute arbitrary code and sharing a memory cache with
the victim) can recover the private keys used in static Diffie-Hellman with
x25519 and x448.

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