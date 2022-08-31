# Elliptic curve performance: NIST vs. Brainpool

## Introduction
Using different elliptic curves has a high impact on the performance of ECDSA, ECDHE and ECDH operations. Each type of curve was designed with a different primary goal in mind, which is reflected in the performance of the specific curves.

The following numbers, measured with Mbed TLS 2.18.0  on a 3.40 GHz Core i7, are only indicative of the relative speed of the various curves. The absolute value depends on your platform. These numbers also use the default settings for speed-memory trade-offs, and you can read more about [Reducing Mbed TLS memory and storage footprint](../how-to/reduce-polarssl-memory-and-storage-footprint.md).

## ECDSA Performance

### NIST Curve Performance
```
ECDSA-secp521r1          :    1093 sign/s
ECDSA-secp384r1          :    1556 sign/s
ECDSA-secp256r1          :    2121 sign/s
ECDSA-secp224r1          :    3103 sign/s
ECDSA-secp192r1          :    4107 sign/s
ECDSA-secp521r1          :     299 verify/s
ECDSA-secp384r1          :     431 verify/s
ECDSA-secp256r1          :     612 verify/s
ECDSA-secp224r1          :     935 verify/s
ECDSA-secp192r1          :    1316 verify/s
```

### Brainpool Curve Performance
```
ECDSA-brainpoolP512r1    :     163 sign/s
ECDSA-brainpoolP384r1    :     361 sign/s
ECDSA-brainpoolP256r1    :     603 sign/s
ECDSA-brainpoolP512r1    :      37 verify/s
ECDSA-brainpoolP384r1    :      81 verify/s
ECDSA-brainpoolP256r1    :     156 verify/s
```

## ECDHE Performance

### NIST Curve Performance
```
ECDHE-secp521r1          :     323 handshake/s
ECDHE-secp384r1          :     466 handshake/s
ECDHE-secp256r1          :     657 handshake/s
ECDHE-secp224r1          :    1017 handshake/s
ECDHE-secp192r1          :    1404 handshake/s
```

### Brainpool Curve Performance
```
ECDHE-brainpoolP512r1    :      37 handshake/s
ECDHE-brainpoolP384r1    :      83 handshake/s
ECDHE-brainpoolP256r1    :     158 handshake/s
```
    
## Why are NIST curves faster than Brainpool curves
Brainpool curves use random primes, as opposed to the quasi-Mersenne primes that NIST curves use. As a result, fast reduction is not possible for Brainpool curves, and this has major consequences for the performance of the different curves.

## Can you optimize Brainpool curves to be as fast as the NIST curves?
Unfortunately, this is not possible. The design decision for Brainpool to use random primes was aimed at:

* avoiding possible patent issues with fast reduction algorithms
* avoiding potential security issues with non-random primes

Brainpool curve performance cannot be adjusted to be equivalent to NIST curve performance.

## Curve25519 support
Bernstein & al have designed high-performance alternatives, such as **Curve25519** for key exchange and **Ed25519** for signatures. Unfortunately, they use slightly different data structures and representations than the other curves, so they haven't been ported yet to TLS and PKIX in Mbed TLS. We do support basic Curve25519 arithmetic though. Their use in TLS has been standardized in [RFC 8422](https://tools.ietf.org/html/rfc8422).
