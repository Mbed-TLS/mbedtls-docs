# How to encrypt and decrypt with RSA

## Reading an RSA key pair

To perform RSA encryption or decryption, you will need an RSA key. In the case of an RSA-2048 decryption, you will need a **2048-bit RSA key**.

More information on generating an RSA key pair is in our article on [RSA key pair generation](/kb/cryptography/rsa-key-pair-generator.md). For now, we assume you have **already generated one or already have one in your possession**.

You can recognize a PEM formatted RSA key pair because it starts with a line with dashes around the string `BEGIN RSA PRIVATE KEY` or `BEGIN PRIVATE KEY`. In the case of the latter, it is not necessarily an RSA key, because `BEGIN PRIVATE KEY` is also used for Elliptic Curve and other types of keys. Information on the PEM formatted key structure can be found in [this article](/kb/cryptography/asn1-key-structures-in-der-and-pem.md).

You will need to start by [adding a random number generator (RNG)](/kb/how-to/add-a-random-generator.md) to your application. In this tutorial, the RNG is the CTR-DRBG generator, and the context is called `ctr_drbg`. The RSA public key is called `our-key.pub`, and the RSA private key is called `our-key.pem`.

Mbed TLS supports two ways for using RSA:

* Directly calling the [RSA module](/rsa-source-code).
* Using the public key layer.

The example will show the second, more advised method.

## Header file

To use the public key layer, you need to include the appropriate header file:
```
#include "mbedtls/pk.h"
```
## RSA 2048-bit encryption in C with Mbed TLS

Start by initializing the public key context and reading in the public key:
```
    int ret = 0;
    mbedtls_pk_context pk;

    mbedtls_pk_init( &pk );

    /*
     * Read the RSA public key
     */
    if( ( ret = mbedtls_pk_parse_public_keyfile( &pk, "our-key.pub" ) ) != 0 )
    {
        printf( " failed\n  ! mbedtls_pk_parse_public_keyfile returned -0x%04x\n", -ret );
        goto exit;
    }
```
<span class="notes">**Note:** There is a [maximum amount of data you can encrypt with RSA](/kb/cryptography/rsa-encryption-maximum-data-size.md). For a 2048 bit RSA key, the maximum you can encrypt is 245 bytes (or 1960 bits).</span>

Store the data to be encrypted and its length in variables. This tutorial uses `to_encrypt` for the data, and its length in `to_encrypt_len`:
```
    unsigned char buf[MBEDTLS_MPI_MAX_SIZE];
    size_t olen = 0;

    /*
     * Calculate the RSA encryption of the data.
     */
    printf( "\n  . Generating the encrypted value" );
    fflush( stdout );

    if( ( ret = mbedtls_pk_encrypt( &pk, to_encrypt, to_encrypt_len,
                                    buf, &olen, sizeof(buf),
                                    mbedtls_ctr_drbg_random, &ctr_drbg ) ) != 0 )
    {
        printf( " failed\n  ! mbedtls_pk_encrypt returned -0x%04x\n", -ret );
        goto exit;
    }
```
The result is in `buf`, with the actual size you should copy out in `olen`.

## RSA 2048-bit decryption in C with Mbed TLS

Decryption is very similar in set-up. The main difference is that you need the **private key** instead of the **public key** to perform the decryption.

Start by initializing the PK context and reading in the 2048-bit private key:
```
    int ret = 0;
    mbedtls_pk_context pk;

    mbedtls_pk_init( &pk );

    /*
     * Read the RSA privatekey
     */
    if( ( ret = mbedtls_pk_parse_keyfile( &pk, "our-key.pem", "" ) ) != 0 )
    {
        printf( " failed\n  ! mbedtls_pk_parse_keyfile returned -0x%04x\n", -ret );
        goto exit;
    }
```
Store data to be decrypted and its length in variables. This tutorial stores the data in `to_decrypt`, and its length in `to_decrypt_len`:
```
    unsigned char result[MBEDTLS_MPI_MAX_SIZE];
    size_t olen = 0;

    /*
     * Calculate the RSA encryption of the data.
     */
    printf( "\n  . Generating the encrypted value" );
    fflush( stdout );

    if( ( ret = mbedtls_pk_decrypt( &pk, to_decrypt, to_decrypt_len, result, &olen, sizeof(result),
                                    mbedtls_ctr_drbg_random, &ctr_drbg ) ) != 0 )
    {
        printf( " failed\n  ! mbedtls_pk_decrypt returned -0x%04x\n", -ret );
        goto exit;
    }
```
So after the call to `mbedtls_pk_decrypt()`, the result is in `result` with the actual size of the decrypted data in `olen`.

<!---",encrypt-and-decrypt-with-rsa,"Article on encrypting and decrypting data with RSA",,"rsa, encrypt, decrypt",published,"2014-05-20 09:21:00",2,26498,"2015-07-24 09:47:00","Paul Bakker"--->
