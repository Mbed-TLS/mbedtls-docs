# Side channel attack on deterministic ECDSA

**Title** |  Side channel attack on deterministic ECDSA
---|---
**CVE** |  CVE-2019-16910
**Date** |  6th September 2019 ( **Updated on 26th September 2019** )
**Affects** |  All versions of Mbed TLS and Mbed Crypto
**Impact** |  If the victim can be tricked to sign the same message<br>repeatedly, the private key may be recoverable through side channels.
**Severity** |  High
**Credit** |  Jack Lloyd

## Vulnerability

Mbed TLS does not have a constant-time/constant-trace arithmetic library and
uses blinding to protect against side channel attacks.

In the ECDSA signature routine previous Mbed TLS versions used the same RNG
object for generating the ephemeral key pair and for generating the blinding
values. The deterministic ECDSA function reused this by passing the RNG object
created from the private key and the message to be signed as prescribed by RFC
6979. This meant that the same RNG object was used whenever the same message
was signed, rendering the blinding ineffective.

## Impact

If the victim can be tricked to sign the same message repeatedly, the blinding
countermeasures are ineffective and the private key can be recovered through
side channels.

## Resolution

Affected users should upgrade to one of the most recent versions of Mbed TLS,
including 2.19.0, 2.16.3 or 2.7.12 or later. Similarly, affected users should
upgrade to the most recent version of Mbed Crypto, including 2.0.0 or later.

Applications using Mbed Crypto should call `mbedtls_ecdsa_sign_det_ext()`
instead of the vulnerable and now deprecated `mbedtls_ecdsa_sign_det()`.

## Workaround

Where possible, we recommend all impacted users upgrade to a newer version of
Mbed TLS or Mbed Crypto.

If this is not possible, as a workaround, disabling deterministic ECDSA
prevents this attack.
