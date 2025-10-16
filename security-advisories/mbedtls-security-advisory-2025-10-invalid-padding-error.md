# Padding oracle through timing of cipher error reporting (CVE-2025-59438)

**Title** | Padding oracle through timing of cipher error reporting
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-59438
**Date** | 15 October 2025
**Affects** | All versions of Mbed TLS up to 3.6.4
**Not affected** | Mbed TLS 3.6.5 and later 3.6 versions, TF-PSA-Crypto 1.0.0 and later
**Impact** | Possible (partial) recovery of plaintext encrypted with CBC-PKCS7
**Severity** | MEDIUM
**Credits** | Beat Heeb from Oberon microsystems AG

## Vulnerability

In symmetric encryption modes that involve padding, if an attacker can submit ciphertexts for decryption and learn whether the padding is valid, this provides partial information about the plaintext. If the attacker can also submit input that the victim encrypts together with a secret, this can allow the attacker to recover the whole secret part. This is known as a padding oracle attack. The attacker may learn the validity of the padding directly or indirectly, for example through timing.

In the Mbed TLS legacy API (`mbedtls_cipher_crypt()`, `mbedtls_cipher_finish()`), the problematic modes are ECB and CBC with any padding other than `NONE`. In the PSA Crypto API (`psa_cipher_decrypt()`, `psa_cipher_finish()`), the problematic algorithm is `PSA_ALG_CBC_PKCS7`.

Mbed TLS takes care to check the padding in constant time inside the legacy cipher modules, so `mbedtls_cipher_crypt()` and `mbedtls_cipher_finish()` are not vulnerable. However, application code may be vulnerable if it handles errors from these functions in a way that is not constant-time.

In the PSA API, when the built-in implementation of CBC-PKCS7 is used, the PSA functions  (`psa_cipher_decrypt()`, `psa_cipher_finish()`) call `mbedtls_cipher_finish()` and translate its error codes into PSA error codes. This translation is not constant-time, and a local unprivileged attacker may be able to observe which error is raised by timing shared resources such as a code cache or a branch predictor.

In the PSA API, when using a driver, there is no error translation. However some code paths inside the library distinguish the error case from the success case, which allows the same attack.

## Impact

Local attackers may be able to recover plaintexts encrypted with CBC-PKCS7 or other symmetric encryption mode using padding when it is decrypted through the PSA API.

Applications using the legacy API to decrypt with padding may be affected through their own error handling.

## Affected versions

All versions of Mbed TLS up to 3.6.4 are affected.

TF-PSA-Crypto 1.0.0beta is also affected.

## Work-around

Applications are not affected if they only accept authenticated ciphertexts for CBC decryption, i.e. if they only use CBC as part of an encrypt-then-MAC construction. (Applications should use AEAD modes instead of CBC-based modes whenever possible.)

## Resolution

Affected users should upgrade to Mbed TLS 3.6.5 or TF-PSA-Crypto 1.0.0 or above.

Additionally, applications using `mbedtls_cipher_crypt()` or `mbedtls_cipher_finish()` with a CBC or EBC mode with padding should review their error handling, and should consider switching to the new function `mbedtls_cipher_finish_padded()` which simplifies the handling of invalid-padding conditions.

Applications doing decryption with `PSA_ALG_CBC_PKCS7` should handle errors carefully if local timing attacks are a concern. (This also applies to asymmetric decryption with `PSA_ALG_RSA_PKCS1V15_CRYPT`.)

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x |
| ------ | -------------- |
| Basic fix | 155de2ab775e77ab6fa81bf2b1e6e63768123bc1, d179dc80a5b13189c79fe4531eacb28698a7a0e9, e74b42832e4af11606ef8aae2c9404b4acaa2c6d, 3b380daedbce9fae3e7ed7e84f18e97876e7e6f3, 04dfd704325a6dbc2a13eb7f418eaca9ae9ca549 |
| With tests and documentation | branch up to 44765c4b9b104ad390d3525626aa4e72320c423b + branch up to cc908ad04c388b50b81fa3b3a8b509cf62797fcf |
