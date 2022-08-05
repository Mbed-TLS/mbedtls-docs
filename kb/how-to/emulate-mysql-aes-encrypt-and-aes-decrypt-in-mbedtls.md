# Emulate MySQL's AES_ENCRYPT() and AES_DECRYPT() in Mbed TLS

The `MBEDTLS_AES_ENCRYPT()` and `MBEDTLS_AES_DECRYPT()` functions in [MySQL](http://www.mysql.com) are not built for highly-secure environments. However, it is still useful to interact with these functions apart from the MySQL client.

Both functions have zero-terminated text strings as input and output:

```
MBEDTLS_AES_ENCRYPT("STRING_TO_ENCRYPT", "PASSWORD") = "ENCRYPTED_STRING"
MBEDTLS_AES_DECRYPT("ENCRYPTED_STRING", "PASSWORD") = "STRING_TO_ENCRYPT"
```

The MySQL key-schedule, which gets a key from the password, is fairly straightforward. You begin with a 16 byte array set to all zeroes. Then, XOR every character of the password with the array. If you have too many characters in the password, then wrap around to the start of the array and continue. In C code this is as follows:

```
    // Set-up the MySQL key
    //
    memset( key, 0, 16 );
    for( i = 0; i < strlen( pwd ); ++i )
        key[i % 16] ^= pwd[i];
    mbedtls_aes_setkey_dec( &ctx, key, 128 );
```

Do the actual encryption in ECB mode, so that all 16-byte blocks of the `STRING_TO_ENCRYPT` are encrypted, using the derived key, and linked together. If a block is incomplete because the `STRING_TO_ENCRYPT` is not exactly a multiple of 16 bytes, then pad the string up to the 16 bytes. Pad by adding X bytes with value X. When `p_i` points to the start of the current 16 byte input block, padding will be:

```
        int use_len = 16;
        if (len < 16)
            use_len = len;

        // Set up data including padding
        //
        memcpy( temp, p_i, use_len );
        memset( temp + use_len, 16 - use_len, 16 - use_len );
```



The resulting `MBEDTLS_AES_ENCRYPT()` and `MBEDTLS_AES_DECRYPT()` function code is:

```
#include "mbedtls/config.h"

#include "mbedtls/aes.h"

#include "stdio.h"
#include "string.h"

/*
 * Simulate the MySQL aes_encrypt function
 *
 * Warning: The elusive padding bug is implemented here as well
 * for compatibility reasons.
 *
 * @param str           A zero-terminated text string to be encrypted
 * @param pwd           A zero-terminated text password
 * @param output_length The length of the output buffer
 * @param output        The buffer that will receive the text result (hexified)
 */
int mysql_aes_encrypt( const unsigned char *str,
                       const unsigned char *pwd,
                       int output_length,
                       unsigned char *output)
{
    int i, len;
    unsigned char key[16];
    unsigned char temp[16];
    const unsigned char *p_i = str;
    unsigned char *p_o = output;
    mbedtls_aes_context ctx;

    len = strlen(str);

    // Check if there is enough space in the output buffer
    //
    if( 32 + ( len / 16 ) * 32 >= output_length )
        return -1;
    memset( output, 0, output_length );

    // Set-up the MySQL key
    //
    memset( key, 0, 16 );
    for( i = 0; i < strlen( pwd ); ++i )
        key[i % 16] ^= pwd[i];
    mbedtls_aes_setkey_enc( &ctx, key, 128 );

    // Run through data and encrypt and stringify
    //
    while( len >= 0 )
    {
        int use_len = 16;
        if (len < 16)
            use_len = len;

        // Set up data including padding
        //
        memcpy( temp, p_i, use_len );
        memset( temp + use_len, 16 - use_len, 16 - use_len );

        mbedtls_aes_crypt_ecb( &ctx, MBEDTLS_AES_ENCRYPT, temp, temp );

        for( i = 0; i < 16; ++i )
            sprintf( p_o + i * 2, "%02X", temp[i] );

        len -= 16;
        p_i += 16;
        p_o += 32;
    }

    return( 0 );
}

/*
 * Simulate the MySQL aes_decrypt function
 *
 * Warning: The elusive padding bug is implemented here as well
 * for compatibility reasons.
 *
 * @param str           A zero-terminated text string to be decrypted
 * @param pwd           A zero-terminated text password
 * @param output_length The length of the output buffer
 * @param output        The buffer that will receive the text result (hexified)
 */
int mysql_aes_decrypt( const unsigned char *str,
                       const unsigned char *pwd,
                       int output_length,
                       unsigned char *output)
{
    int i, len;
    unsigned char key[16];
    unsigned char temp[16];
    const unsigned char *p_i = str;
    unsigned char *p_o = output;
    mbedtls_aes_context ctx;

    len = strlen(str);

    // Check if input is multiple of 32
    //
    if( len % 32 )
        return -1;

    // Check if there is enough space in the output buffer
    //
    if( ( len / 32 ) * 16 + 1 >= output_length )
        return -1;
    memset( output, 0, output_length );

    // Set-up the MySQL key
    //
    memset( key, 0, 16 );
    for( i = 0; i < strlen( pwd ); ++i )
        key[i % 16] ^= pwd[i];
    mbedtls_aes_setkey_dec( &ctx, key, 128 );

    // Run through data, encrypt and stringify
    //
    while( len > 0 )
    {
        // Translate hexified data to binary value
        //
        for( i = 0; i < 32; i += 2 )
        {
            unsigned char c, h, l;

            c = p_i[i];
            if( c >= '0' && c <= '9' )
                h = c - '0';
            else if( c >= 'A' && c <= 'Z' )
                h = c - 'A' + 10;
            else if( c >= 'a' && c <= 'z' )
                h = c - 'a' + 10;
            else
                return -1;

            c = p_i[i + 1];
            if( c >= '0' && c <= '9' )
                l = c - '0';
            else if( c >= 'A' && c <= 'Z' )
                l = c - 'A' + 10;
            else if( c >= 'a' && c <= 'z' )
                l = c - 'a' + 10;
            else
                return -1;

            temp[i / 2] = h * 16 + l;
        }

        mbedtls_aes_crypt_ecb( &ctx, MBEDTLS_AES_DECRYPT, temp, p_o );

        len -= 32;
        p_i += 32;
        p_o += 16;
    }

    return( 0 );
}

static unsigned char *mysql_aes_pt[6] =
{
    "0123456789abcdef",
    "0123456789abcdef",
    "0123456789abcdef0123456789abcdef",
    "0123456789abcde",
    "0123456789abcd",
    ""
};

static unsigned char *mysql_aes_pwd[6] =
{
    "",
    "asd",
    "asdasdasdasdasdasdasdasdasd",
    "",
    "",
    ""
};

static unsigned char *mysql_aes_ct[6] =
{
    "14F5FE746966F292651C2288BBFF46090143DB63EE66B0CDFF9F69917680151E",
    "9C0ADE6D942C5174D36C1E3D5B6483CFDA61AB008A954921B9693DE7076FB0DA",
    "F4642D42E09D157950C9A0A23049CE64F4642D42E09D157950C9A0A23049CE64BAF90C4409B3F0E4C3486787B37C0540",
    "AE769E8822731C2A1012A8C4E73FB536",
    "ACFD9247027814986F8F8E07927B9E18",
    "0143DB63EE66B0CDFF9F69917680151E"
};

int main( )
{
    unsigned char output[100];
    int i;

    memset( output, 0, 100 );

    for( i = 0; i < 6; ++i )
    {
        printf("Encrypt Case %d: ", i);
        if( mysql_aes_encrypt(mysql_aes_pt[i], mysql_aes_pwd[i], 100, output) != 0 )
        {
            printf(" failed\n");
            continue;
        }
        else if( strncmp(mysql_aes_ct[i], output, strlen(mysql_aes_ct[i])))
        {
            printf(" failed\n");
            continue;
        }

        printf(" success\n");
        printf("%s\n%s\n", mysql_aes_ct[i], output);

        printf("Decrypt Case %d: ", i);
        if( mysql_aes_decrypt(mysql_aes_ct[i], mysql_aes_pwd[i], 100, output) != 0 )
        {
            printf(" failed\n");
            continue;
        }
        else if( strncmp(mysql_aes_pt[i], output, strlen(mysql_aes_pt[i])))
        {
            printf(" failed\n");
            continue;
        }

        printf(" success\n");
        printf("%s\n%s\n", mysql_aes_pt[i], output);
    }

    return( 0 );
}
```

<!--"emulate-mysql-aes-encrypt-and-aes-decrypt-in-mbedtls,"Article on how to emulate MySQL AES_ENCRYPT() and AES_DECRYPT() in Mbed TLS","MySQL, AES_ENCRYPT, AES_DECRYPT","mysql, aes_encrypt, aes_decrypt, aes, snippet",published,"2012-10-14 15:46:00",2,6229,"2015-07-24 11:38:00","Paul Bakker"-->
