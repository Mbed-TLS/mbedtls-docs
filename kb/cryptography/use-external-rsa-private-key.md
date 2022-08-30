# Using an external RSA private key

## Use case

The RSA private key is not available in exported form. It is located inside a smartcard or in a secure hardware module. Therefore, you are not able to load it the usual way.

## Providing your own functions

Mbed TLS is designed for this, and allows you to set your own functions to be used for RSA decryption and signing during the SSL handshake.

Set these functions by using `mbedtls_pk_setup_rsa_alt()`. This allows your application to provide an arbitrary blob as your RSA private key, accept function pointers performing decryption and signature, and return the key size, as above.

You can then use the normal `mbedtls_set_own_cert()` function. From the perspective of the SSL module, the external RSA private key is just another PK context.

## PKCS#11

If you are using a smartcard, you don't have to write your own logic. You can use the `libpkcs11-helper` library.

Mbed TLS includes a helper class for using the `libpkcs11-helper` when you enable `MBEDTLS_PKCS11_C` in `config.h`. See [How do I configure Mbed TLS](../compiling-and-building/how-do-i-configure-mbedtls.md).
