# Local side channel attack on RSA and static Diffie-Hellman

**Title** |  Local side channel attack on RSA and static Diffie-Hellman
---|---
**CVE** |  (none)
**Date** |  1st of September, 2020
**Affects** |  All versions of Mbed TLS and Mbed Crypto
**Impact** |  A powerful local attacker can extract the private key
**Severity** |  High
**Credit** |  (found internally following previous work from Alejandro Cabrera<br>Aldaya and Billy Bob Brumley)

## Vulnerability

RSA and static Diffie-Hellman use a counter-measure known as base blinding
(see [section 10 of this
paper](https://paulkocher.com/doc/TimingAttacks.pdf#page=8)) in order to
prevent (adaptative) chosen-input attacks on modular exponentiation. The
counter-measure works by multiplying the base with a secret value before the
modular exponentiation, then multiplying the result with a well-chosen value
to recover the actual result. In order to save on computation costs, these
blinding/unblinding values are not drawn at random for each operation; instead
they're drawn at random the first time only, then updated in a deterministic
way. It is thus crucial that those values are not leaked: otherwise the
adversary could predict future blinding values and retain the ability to
choose the base passed to the modular exponentiation operation.

While generating the blinding/unblinding values, a modular inverse is
computed, and a [recent paper](https://eprint.iacr.org/2020/055.pdf) showed
that our modular inverse function (more precisely, our GCD function which it
calls) is vulnerable to a single-trace side-channel attack by powerful local
adversaries. Such an adversary could recover the initial blinding/unblinding
values, predict future values, and then proceed to use any known chosen-input
attack that base blinding was supposed to protect against, with consequences
ranging up to full private key compromise.

## Impact

An attacker with access to precise enough timing and memory access information
(typically an untrusted operating system attacking a secure enclave such as
SGX or the TrustZone secure world) can recover the private keys used in RSA or
static (finite-field) Diffie-Hellman operations.

## Resolution

Affected users will want to upgrade to Mbed TLS 2.24.0, 2.16.8 or 2.7.17
depending on the branch they're currently using.

## Work-around

None.
