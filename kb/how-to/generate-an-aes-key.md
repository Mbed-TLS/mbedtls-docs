# Generating an AES key

An AES key is a random bitstring of the right length.

* For a 128-bit AES key you need 16 bytes.
* For a 256-bit AES key you need 32 bytes.

If you need to generate your own AES key for encrypting data, you should use a good random source. The strength of the key depends on the unpredictability of the random.

Mbed TLS includes the [CTR-DRBG module](/ctr-drbg-source-code) and an [Entropy Collection module](/entropy-source-code) to help you with making an AES key generator for your key.

To use the AES generator, you need to have the modules enabled in the `config.h` files (`MBEDTLS_CTR_DRBG_C` and `MBEDTLS_ENTROPY_C`), see [How do I configure Mbed TLS](/kb/compiling-and-building/how-do-i-configure-mbedtls.md).

Include the following headers in your code:

    #include "mbedtls/entropy.h"
    #include "mbedtls/ctr_drbg.h"

Then add the following variable definitions to your code:

    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_entropy_context entropy;
    unsigned char key[32];

    char *pers = "aes generate key";
    int ret;

The personalization string needs to be unique to your application to add randomness to your random sources.

## Creating the AES key

You need to initialize the entropy pool and the random source and extract data for your key. In this case we generate 32 bytes (256 bits) of random data.

    mbedtls_entropy_init( &entropy );

    mbedtls_ctr_drbg_init( &ctr_drbg );

    if( ( ret = mbedtls_ctr_drbg_seed( &ctr_drbg, mbedtls_entropy_func, &entropy,
        (unsigned char *) pers, strlen( pers ) ) ) != 0 )
    {
        printf( " failed\n ! mbedtls_ctr_drbg_init returned -0x%04x\n", -ret );
        goto exit;
    }

    if( ( ret = mbedtls_ctr_drbg_random( &ctr_drbg, key, 32 ) ) != 0 )
    {
        printf( " failed\n ! mbedtls_ctr_drbg_random returned -0x%04x\n", -ret );
        goto exit;
    }

Now you can use the data in `key` as a 256-bit AES key.

<!-- This guide from Mbed TLS explains how to generate an AES key.","AES key generation, generate AES key, AES key","aes, aes key, key generation, snippet, entropy, randomness, random -->
