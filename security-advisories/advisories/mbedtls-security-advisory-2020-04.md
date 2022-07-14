# Side channel attack on ECDSA

**Title** |  Side channel attack on ECDSA
---|---
**CVE** |  CVE-2020-10932
**Date** |  14th of April, 2020
**Affects** |  All versions of Mbed TLS and Mbed Crypto
**Impact** |  A local attacker can extract the private key
**Severity** |  High
**Credit** |  Alejandro Cabrera Aldaya, Billy Brumley and Cesar Pereida Garcia

## Vulnerability

The modular inverse operation as implemented in Mbed TLS is vulnerable to a
single-trace side channel attack [discovered by Alejandro Cabrera Aldaya and
Billy Brumley](https://eprint.iacr.org/2020/055) which may allow a local
adversary to recover the full value of the operand. (Some consequences of this
attack on [RSA](mbedtls-security-advisory-2020-02.md) and
[ECDSA](mbedtls-security-advisory-2019-12.md) were fixed in previous releases.)

Mbed TLS, like most libraries implementing ECC, uses projective coordinates to
represent points internally. It is [known](https://eprint.iacr.org/2003/191)
that leaking the coordinates allows an attacker to recover a few bits of the
private value. The conversion back from projective coordinates involves a
modular inverse operation and is therefore vulnerable to the above new attack.
An attacker who is able to obtain the coordinates from several ECDSA signature
operations with the same key can eventually recover the private key through a
lattice attack.

A complete description of the attack is available in [this
paper](https://eprint.iacr.org/2020/432.pdf).

## Impact

An attacker with access to precise enough timing and memory access information
(typically an untrusted operating system attacking a secure enclave such as
SGX or the TrustZone secure world) can fully recover an ECDSA private key
after observing a number of signature operations.

## Resolution

Affected users will want to upgrade to Mbed TLS 2.22.0, 2.16.6 or 2.7.15
depending on the branch they're currently using.

## Work-around

There is no known work-around. Affected users need to upgrade.
