# Local side channel attack on classical CBC decryption in (D)TLS

**Title** |  Local side channel attack on classical CBC decryption in (D)TLS
---|---
**CVE** |  CVE-2020-16150
**Date** |  1st of September, 2020
**Affects** |  All versions of Mbed TLS
**Impact** |  A local attacker can extract portions of the plaintext
**Severity** |  High
**Credit** |  Tuba Yavuz, Farhaan Fowze, Ken (Yihan) Bai, Grant Hernandez,
Kevin Butler and Dave Tian.

## Vulnerability

When decrypting/authenticating (D)TLS record in a connection using a CBC
ciphersuite without the Encrypt-then-Mac extension [RFC
7366](https://tools.ietf.org/html/rfc7366), Mbed TLS used dummy rounds of the
compression function associated with the hash used for HMAC in order to hide
the length of the padding to remote attackers, as recommended in the [original
Lucky Thirteen paper](http://www.isg.rhul.ac.uk/tls/TLStiming.pdf).

A local attacker who is able to observe the state of the cache could monitor
the presence of `mbedtls_md_process()` in the cache in order to determine when
the actual computation ends and when the dummy rounds start. This is a
reliable target as it's always called at least once, in response to a
[previous
attack](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.700.1952&rep=rep1&type=pdf).
The attacker can then continue with one of many well-documented Lucky 13
variants.

In order to fix this, as well as future variants of Lucky 13 relying on a
local attacker's abilities, the implementation was changed to compute the
expected MAC, extract the transmitted MAC and compare them, using constant
memory access patterns and execution flow.

## Impact

An local attacker with access to enough information about the state of the
cache (including, but not limited to, an untrusted operating system attacking
a secure enclave such as SGX or the TrustZone secure world) can recover
portions of the plaintext of a (D)TLS record.

## Resolution

Affected users will want to upgrade to Mbed TLS 2.24.0, 2.16.8 or 2.7.17
depending on the branch they're currently using.

## Work-around

Users are encouraged to use AEAD ciphersuites (CHACHA20-POLY1305, GCM, CCM)
whenever possible, or it they have to use CBC, to enable use of the Encrypt-
then-Mac extension on both sides of the connection.
