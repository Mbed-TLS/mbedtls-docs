# Timing side channel in private key RSA operations.

**Title** |  Timing side channel in private key RSA operations.
---|---
**CVE** |  CVE-2024-23170
**Date** |  10 January 2024
**Affects** |  All versions of Mbed TLS up to and including 2.28.6 and 3.5.1
**Impact** |  Potential recovery of plaintext
**Severity** |  Medium
**Credit** |  Hubert Kario (Red Hat)

## Vulnerability

Mbed TLS is vulnerable to a timing side channel in private key RSA operations.
This side channel could be sufficient for an attacker to recover the plaintext.
A local attacker or a remote attacker who is close to the victim on the network
might have precise enough timing measurements to exploit this. It requires the
attacker to send a large number of messages for decryption. For details,
see [Everlasting ROBOT: the Marvin Attack](https://eprint.iacr.org/2023/1442.pdf), Hubert Kario (Red Hat).

## Impact

An attacker meeting the conditions above could potentially recover the
plaintext.

## Resolution

Affected users will want to upgrade to Mbed TLS 3.5.2 or 2.28.7 depending on the
branch they're currently using.

## Work-around

There is no known work-around. Affected users need to upgrade.