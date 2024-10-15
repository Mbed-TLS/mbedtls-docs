# Buffer underrun in pkwrite when writing an opaque key pair

**Title** | Buffer underrun in pkwrite when writing an opaque key pair
--------- | ----------------------------------------------------------
**CVE** | CVE-2024-49195
**Date** | 14 October 2024
**Affects** | Mbed TLS 3.5.0 to 3.6.1 included
**Severity** | HIGH

## Vulnerability

The functions `mbedtls_pk_write_key_der()` and `mbedtls_pk_write_key_pem()` can cause a buffer underrun when the output buffer is too small in some cases. In all problematic cases:

* The compile-time option `MBEDTLS_USE_PSA_CRYPTO` is enabled.
* The PK context contains an opaque key (`MBEDTLS_PK_OPAQUE`, typically set up with `mbedtls_pk_setup_opaque()`).

The following cases are problematic:

* Writing an elliptic curve key pair with `mbedtls_pk_write_key_der()`, when the compile-time option `MBEDTLS_ECP_C` is enabled, with an output buffer that is smaller than the representation of the public key as an uncompressed point.
* Writing an RSA key pair with `mbedtls_pk_write_key_der()`, with an output buffer that is smaller than the actual output.
* Writing an RSA key pair with `mbedtls_pk_write_key_pem()`, if `MBEDTLS_MPI_MAX_SIZE <= 420`.

Each of these cases trigger a code path where the output is first written safely into an intermediate buffer. The output is then copied to the destination buffer supplied by the application code, without checking that the buffer is large enough.

## Impact

The consequence of the vulnerability is a buffer underrun of up to the size of the key representation. Depending on the location of the application buffer, this can result in stack or heap corruption.

## Affected versions

The vulnerability is present in Mbed TLS 3.5.x, Mbed TLS 3.6.0 and Mbed TLS 3.6.1. Earlier versions had a different implementation of the problematic cases and are not affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.2.

## Work-around

Calling `mbedtls_pk_write_key_der()` with a buffer that is large enough for the content is always safe. Furthermore, `PSA_EXPORT_KEY_PAIR_MAX_SIZE` is always a safe buffer size. There are no unsafe calls to `mbedtls_pk_write_key_der()` within Mbed TLS itself, except when calling `mbedtls_pk_write_key_pem()` in the configurations described below.

`mbedtls_pk_write_key_pem()` is safe when `MBEDTLS_MPI_MAX_SIZE >= 421` or when `MBEDTLS_USE_PSA_CRYPTO` is disabled.

These functions are only vulnerable when called on PK contexts of type `MBEDTLS_PK_OPAQUE`. Copying the key with `mbedtls_pk_copy_from_psa` and calling `mbedtls_pk_write_key_xxx()` on the resulting non-opaque key is safe.
