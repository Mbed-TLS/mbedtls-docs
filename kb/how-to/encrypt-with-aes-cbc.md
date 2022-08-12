# Encrypt data with AES-CBC mode

To encrypt data with [AES](/aes-source-code), you need a key. If you are not familiar with key generation, please check out [How to generate an AES key](/kb/how-to/generate-an-aes-key.md) for more information.

<span class="notes">**Note:** Please understand that only encrypting data with AES-CBC does not keep the data safe from modification or viewing. You still have to protect the **key** from others and the **integrity** of the data. This article only shows you how to use the [AES API](/api/aes_8h.html) to encrypt some data with the AES-CBC mode.</span>

To start using AES, add the header file for the module to your file:

```
#include "mbedtls/aes.h"
```

Declare the variables needed for AES encryption:

```
mbedtls_aes_context aes;

unsigned char key[32];
unsigned char iv[16];

unsigned char input [128];
unsigned char output[128];

size_t input_len = 40;
size_t output_len = 0;
```

This examples assumes you've filled the variable named **key** with the 32 bytes of the AES key (see [How to generate an AES key](/kb/how-to/generate-an-aes-key.md)), **iv** with 16 bytes of random data for use as the Initialization Vector (IV) and **input** with 40 bytes of input data, and zeroized the rest of **input**.

The **CBC** mode for AES assumes that you provide data in blocks of 16 bytes. Because there are only 40 bytes of data, you have to extend the input to contain 48 bytes of data, instead. There are multiple ways to pad input data. One is to add zeroes to the end. This is only secure if you also transmit the original length of the input data (40 in this case) securely to the other side, as well. This example uses padding with zeroes.

First, initialize the AES context with your **key**, and then encrypt the data (with padding) to the output buffer with your **iv**:

```
mbedtls_aes_setkey_enc( &aes, key, 256 );
mbedtls_aes_crypt_cbc( &aes, MBEDTLS_AES_ENCRYPT, 48, iv, input, output );
```

The first 48 bytes of the **output** buffer contain the encrypted data. This data is only protected for confidentiality purposes. You need to send the length of the input data, the IV and the output buffer to the other side while protecting the integrity of those values. In addition, the other side needs the key without anybody ever knowing it. Usually this means making a hash over the length of the input data, the IV and the output buffer and encrypting this hash and the AES key with the public RSA key of the other party using the PKCS#1 encrypt function.

<!---encrypt-with-aes-cbc,"This guide from Mbed TLS explains how to encrypt data with AES-CBC mode.","AES-CBC, CBC mode","aes, cbc, snippet, encryption, decryption, encrypt, decrypt, iv, rsa",published,"2012-12-11 14:50:00",2,36173,"2017-04-24 11:20:00","Paul Bakker"--->
