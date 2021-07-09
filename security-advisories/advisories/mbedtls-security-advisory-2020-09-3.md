# Protocol weakness in DHE-PSK key exchange

**Title** |  Protocol weakness in DHE-PSK key exchange
---|---
**CVE** |  Unknown
**Date** |  1st of September, 2020
**Affects** |  All versions of Mbed TLS
**Impact** |  An active network attacker can learn the size of the pre-shared
key
**Severity** |  Low
**Credit** |  Robert Merget, Marcus Brinkmann, Nimrod Aviram and Juraj
Somorovsky

## Vulnerability

This is an advisory of a security vulnerability in the TLS specification,
which has very limited impact on Mbed TLS: the Raccoon attack (for details see
the [website](https://raccoon-attack.com/) and the [paper](https://raccoon-
attack.com/RacoonAttack.pdf)).

In the TLS protocol, the calculation of the premaster secret from the finite-
field Diffie-Hellman (FFDH) shared secret strips the leading zero bytes. If
the Diffie-Hellman private key is reused, side channels during this
calculation may allow an adversary to recover bits of the premaster secret.
Since Mbed TLS does not support static finite-field Diffie-Hellman nor the
reuse of ephemeral keys, the library is not vulnerable to this class of
attacks.

When using Diffie-Hellman combined with a pre-shared key (DHE-PSK cipher
suites), the premaster secret is constructed by concatenating the pre-shared
key with other elements. Side channels during this calculation may reveal the
length of the pre-shared key. Mbed TLS is vulnerable to this attack.

Elliptic curve Diffie-Hellman (ECDH, including ECDHE) is not affected in the
same way because the shared secret is used directly without any truncation.
There is a potential implementation flaw if the calculation of the shared
secret truncates leading zero digits and then pads them back, leading to the
same vulnerabilities as in the FFDH case. Mbed TLS copies the shared secret
directly without inspecting the leading digits, so it is not vulnerable to
this class of attacks.

## Impact

Adversaries may be able to learn the size of the pre-shared key in used DHE-
PSK cipher suites.

## Resolution

It is unusual to rely on the confidentiality of the length of a key. Even the
minimum length of the key needs to be sufficiently large not to be vulnerable
to brute-force attacks. As a consequence, we do not plan to mitigate this
issue in Mbed TLS.

## Work-around

If you use a DHE-PSK cipher suite, treat the length of the pre-shared key as a
public quantity. If you have privacy concerns, always use a pre-shared key of
the same length.

### Like this?

**Section:**
Security Advisories

**Author:**
Manuel Pégourié-Gonnard

**Published:**
Sep 1, 2020

**Last updated:**
Sep 10, 2020