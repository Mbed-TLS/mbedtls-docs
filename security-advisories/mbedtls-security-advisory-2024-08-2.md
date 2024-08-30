# Stack buffer overflow in ECDSA signature conversion functions

**Title** | Stack buffer overflow in ECDSA signature conversion functions
--------- | -----------------------------------------------------
**CVE** | TODO
**Date** | TODO
**Affects** | Mbed TLS 3.6.0
**Severity** | High

## Vulnerability

In Mbed TLS 3.6.0, the functions `mbedtls_ecdsa_der_to_raw()` and `mbedtls_ecdsa_raw_to_der()` do not correctly validate their `bits` argument. If the value of that argument is larger than the bit-length of the largest supported curve, these functions may overflow a buffer on the stack with content copied from their input parameter.

When `MBEDTLS_PSA_CRYPTO_C` is enabled, the maximum safe value of `bits` is the size of the largest curve supported by the PSA API. All curves supported by the legacy API (`ecp.h`, `ecdh.h`, `ecdsa.h`, `ecjpake.h`, `pk.h`) are also supported by the PSA API, thus any curve size supported in Mbed TLS is safe. However, code that calls these functions without ensuring that `bits` corresponds to a supported curve is vulnerable.

When `MBEDTLS_PSA_CRYPTO_C` is disabled, in some configurations, the functions use a 0-size buffer internally. If this is not detected at compile time, the functions would overflow their internal buffer for all correct inputs. These functions are declared in `mbedtls/psa_util.h` and were intended for use together with the PSA API, but they were not excluded from builds without PSA.

All the calls to these functions made inside Mbed TLS are safe.

## Impact

Applications that call `mbedtls_ecdsa_der_to_raw()` or `mbedtls_ecdsa_raw_to_der()` on attacker-controlled input are vulnerable to a stack buffer overflow with attacker-chosen content. Note that to provoke the attack, the attacker needs to control the declared curve bit-size, not just the buffer size and content.

## Resolution

Affected users will want to upgrade to Mbed TLS 3.6.1.

## Work-around

Code that calls `mbedtls_ecdsa_der_to_raw()` and `mbedtls_ecdsa_raw_to_der()` in Mbed TLS 3.6.0 is safe if `MBEDTLS_PSA_CRYPTO_C` is enabled and the calling code first ensures that the `bits` parameter is the bit-size of a curve that is supported in the build of Mbed TLS.
