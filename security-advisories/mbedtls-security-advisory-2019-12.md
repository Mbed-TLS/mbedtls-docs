# Side channel attack on ECDSA

**Title** |  Side channel attack on ECDSA
---|---
**CVE** |  CVE-2019-18222
**Date** |  15th January 2020 ( **Updated on 27th January 2020** )
**Affects** |  All versions of Mbed TLS and Mbed Crypto
**Impact** |  The private key is recoverable through side channels.
**Severity** |  High
**Credit** |  Alejandro Cabrera Aldaya and Billy Brumley

## Vulnerability

Our bignum implementation is not constant time/constant trace, so side channel
attacks can retrieve the blinded value, factor it (as it is smaller than RSA
keys and not guaranteed to have only large prime factors), and then, by brute
force, recover the key. Reported by Alejandro Cabrera Aldaya and Billy
Brumley.

## Impact

If the adversary is in the position to launch a cache attack, then they may be
able to recover the private key.

## Resolution

Affected users should upgrade to one of the most recent versions of Mbed TLS,
including 2.20.0, 2.16.4 or 2.7.13 or later. Similarly, affected users should
upgrade to the most recent version of Mbed Crypto, including 3.0.1 or later.

**edit:** Earlier, this document falsely stated that Mbed Crypto 3.0.0 fixes
this issue. This is not true, Mbed Crypto 3.0.1 is the earliest version with
the fix. Users should upgrade to Mbed Crypto 3.0.1 or later.

## Workaround

There are no known workarounds.
