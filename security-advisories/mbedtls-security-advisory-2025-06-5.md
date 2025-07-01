# Timing side-channel in block cipher decryption with PKCS#7 padding

**Title** | Timing side-channel in block cipher decryption with PKCS#7 padding
--------- | -----------------------------------------------------------------
**CVE** | CVE-2025-49087
**Date** | 30 June 2025
**Affects** | All versions of Mbed TLS from 3.6.1 to 3.6.3 inclusive
**Not affected** | Mbed TLS 3.6.4 and later 3.6 versions and upcoming TF-PSA-Crypto 1.0 and later versions
**Impact** | Plaintext recovery
**Severity** | MEDIUM
**Credit** | Ka Lok Wu from Stony Brook University and Doria Tang from The Chinese University of Hong Kong

## Vulnerability

Mbed TLS is vulnerable to a timing side channel attack on its implementation of PKCS#7 padding removal. An attacker with access to timing information and a decryption oracle can recover the last byte of each plaintext block. If some portion of the plaintext is controlled by the attacker as is often the case, the whole plaintext can be recovered.

The function that performs PKCS#7 padding removal first checks that the last byte of the plaintext is in the range (0, BLOCKSIZE], where BLOCKSIZE is the block size of the cipher. If the last byte is outside of this range, the function exits early, creating a timing oracle. An attacker with access to timing information can use this oracle to recover the value of the last byte of the plaintext by requesting the decryption of manipulated ciphertexts. By truncating the ciphertext, they can recover the value of the last byte of an arbitrary block.

Any applications using the PKCS#7 padding mode are vulnerable (when `PSA_ALG_CBC_PKCS7` or `MBEDTLS_CIPHER_PADDING_PKCS7` is enabled).

## Impact

Full plaintext recovery.

## Affected versions

All versions of Mbed TLS from 3.6.1 up to 3.6.3 are affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.4 or upcoming TF-PSA-Crypto 1.0 or later.

## Work-around

Do not use the PKCS#7 padding scheme with block ciphers. Choose an alternative padding scheme when calling `mbedtls_cipher_set_padding_mode()`. Other possible padding schemes are as follows:

* `MBEDTLS_PADDING_ONE_AND_ZEROS` - ISO/IEC 7816-4 padding
* `MBEDTLS_PADDING_ZEROS_AND_LEN` - ANSI X.923 padding
* `MBEDTLS_PADDING_ZEROS` - Zero padding (not reversible)
* `MBEDTLS_PADDING_NONE` - Never pad (full blocks only)

If using PSA, choose a different cipher to `PSA_ALG_CBC_PKCS7`, depending on your application.
