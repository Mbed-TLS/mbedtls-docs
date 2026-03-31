# FFDH: lack of contributory behaviour due to improper input validation (CVE-2026-34872)

**Title** | FFDH: lack of contributory behaviour due to improper input validation
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-34872
**Date** | 31 March 2026
**Affects** | TF-PSA-Crypto 1.0 and all versions of Mbed TLS up to 3.6.5
**Not affected** | TF-PSA-Crypto 1.1 and Mbed TLS 3.6.6
**Impact** | FFDH does not guarantee contributory behaviour, which some
protocols may require
**Severity** | MEDIUM
**Credits** | Found independently by Eva Crystal (0xiviel) and another reporter

## Vulnerability

When doing key agreement with `PSA_ALG_FFDH` using the built-in driver, the
peer's public key is not properly validated as required by RFC 7919 and NIST
SP800-56A. As a result, the peer can force the resulting shared secret into a
small set of values. This is known as lack of contributory behaviour.

Whether this is a problem or not depends on the overall protocol in which FFDH
is used.

TLS 1.3 is not affected as the master secret depends on the entire handshake
transcript, including random bytes provided by each party, so this does not
allow one of the peers to force the master secret into a small set of values.

TLS 1.2 is not affected for a very different reason: the checks are only
realistic on well-known groups that are known to use safe primes, but TLS 1.2
allows any server-provided group, making the relevant checks effectively
impossible on the client.

## Impact

The direct impact is that the peer can force the FFDH shared secret into a small
set of values. The larger impact depends on the overall protocol in which FFDH
is used.

## Affected versions

TF-PSA-Crypto 1.0.0 is affected.

All versions of Mbed TLS up to and including 3.6.5 are affected.

## Work-around

There is no convenient workaround. However, applications doing FFDH as part of a
protocol that requires contributory behaviour could check if the string passed
as the `peer_key` argument of `psa_key_agreement()`, `psa_raw_key_agreement()`,
`psa_key_derivation_key_agreement()` represents a number in the range [2, p-2].
For example, when using the 2048-bit prime, the bounds are represented by the
following byte strings:
```
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002
ffffffffffffffffadf85458a2bb4a9aafdc5620273d3cf1d8b9c583ce2d3695a9e13641146433fbcc939dce249b3ef97d2fe363630c75d8f681b202aec4617ad3df1ed5d5fd65612433f51f5f066ed0856365553ded1af3b557135e7f57c935984f0c70e0e68b77e2a689daf3efe8721df158a136ade73530acca4f483a797abc0ab182b324fb61d108a94bb2c8e3fbb96adab760d7f4681d4f42a3de394df4ae56ede76372bb190b07a7c8ee0a6d709e02fce1cdf7e2ecc03404cd28342f619172fe9ce98583ff8e4f1232eef28183c3fe3b1b4c6fad733bb5fcbc2ec22005c58ef1837d1683b2c6f34a26c1b2effa886b423861285c97fffffffffffffffd
```
The byte string passed as the `peer_key` argument should `memcmp() >= 0` to the
lower bound and `memcmp() <= 0` to the upper bound.
Users who want to use this approach will need to look up the primes for the
sizes they are using in [RFC
7919](https://datatracker.ietf.org/doc/html/rfc7919).

In Mbed TLS 3.6, the legacy API `mbedtls_dhm_calc_secret()` is not affected.

In all versions, applications are only affected if they use the PSA API to
perform FFDH as part of a larger protocol that expects contributory behaviour
from FFDH.

## Resolution

Affected users should upgrade to TF-PSA-Crypto 1.1.0 or later, or Mbed TLS 3.6.6
or later.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.x | Mbed TLS 4.x |
| ------ | -------------- | ----------------- | ------------ |
| Basic fix | 7d9f1b55fc88 | 274c257439fa | n/a |
| With tests | 01b04ab723b7..199d4d93808b | 1d9b4ad314a8..9831eb7ec30e | n/a |
