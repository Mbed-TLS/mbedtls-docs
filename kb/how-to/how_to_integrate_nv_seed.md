# Porting the non-volatile (NV) seed

If a hardware platform cannot take advantage of a hardware entropy source, alternatives have to be considered. A strong entropy source is crucial for the security of cryptographic and TLS operations. For platforms that support non-volatile (NV) memory, an option is to use the NV seed entropy source that Mbed TLS provides.

This feature can be used *in addition* to a hardware entropy source as well, however, it is not mandatory as the hardware entropy source should be strong enough.

This makes Mbed TLS use a fixed amount of entropy as a seed and update this seed each time entropy is gathered with an Mbed TLS entropy collector for the first time. In a simple case it means that the seed is updated after reset at the start of the first TLS connection.

# Enabling NV seed entropy source support

You should define `MBEDTLS_ENTROPY_NV_SEED` in your configuration, as described in [this article](/kb/compiling-and-building/how-do-i-configure-mbedtls.md). This ensures the entropy pool knows it can use the NV seed entropy source. You should set the following functions to make the entropy collector call them:

    int (*mbedtls_nv_seed_write)( unsigned char *buf, size_t buf_len );
    int (*mbedtls_nv_seed_read)( unsigned char *buf, size_t buf_len );

There are several options for how to set these functions:

1. Using the standard libc functions.
1. Using platform specific functions.
1. Defining platform specific functions.

All these options require `MBEDTLS_ENTROPY_NV_SEED` to be defined.

## Using the standard libc functions

This option should be used if your platform supports standard libc file functions to read from and write to a predefined file name.

1. Define `MBEDTLS_PLATFORM_STD_NV_SEED_FILE` as your seed file name. Default is "seedfile".
1. Verify that `MBEDTLS_PLATFORM_NO_STD_FUNCTIONS` is undefined.
1. Define `MBEDTLS_FS_IO`.

## Using platform specific functions

This option can be used if your platform has its own file system functionality, but the functions have the same prototypes as `mbedtls_nv_seed_write()` and `mbedtls_nv_seed_read()`.

In your configuration file:
1. Define `MBEDTLS_PLATFORM_NV_SEED_ALT` to suggest that there are alternative implementations for the NV seed functions.
1. Define `MBEDTLS_PLATFORM_STD_NV_SEED_READ` as your platform's file system read function.
1. Define `MBEDTLS_PLATFORM_STD_NV_SEED_WRITE` as your platform's file system write function.

## Defining platform specific functions

This option should be used if your platform's file system functions do not share the same prototypes as `mbedtls_nv_seed_write()` and `mbedtls_nv_seed_read()` and you need to write wrapper functions to call your platform's file functions.

1. Define `MBEDTLS_PLATFORM_NV_SEED_ALT` in your configuration file to suggest that there are alternative implementations for the NV seed functions.
1. Implement a function for reading from your file system, which receives as parameters a buffer, the buffer's size and returns the number of bytes read, or an error on failure.
1. Implement a function for writing to your file system, which receives as parameters a buffer, number of bytes to write and the number of bytes written.
1. On your platform's initialization, call `mbedtls_platform_set_nv_seed()` with your implemented functions as parameters.

Example:

```
int mbedtls_platform_std_nv_seed_read( unsigned char *buf, size_t buf_len )
{
    FILE *file;
    size_t n;

    if( ( file = fopen( MBEDTLS_PLATFORM_STD_NV_SEED_FILE, "rb" ) ) == NULL )
        return( -1 );

    if( ( n = fread( buf, 1, buf_len, file ) ) != buf_len )
    {
        fclose( file );
        mbedtls_platform_zeroize( buf, buf_len );
        return( -1 );
    }

    fclose( file );
    return( (int)n );
}

int mbedtls_platform_std_nv_seed_write( unsigned char *buf, size_t buf_len )
{
    FILE *file;
    size_t n;

    if( ( file = fopen( MBEDTLS_PLATFORM_STD_NV_SEED_FILE, "w" ) ) == NULL )
        return -1;

    if( ( n = fwrite( buf, 1, buf_len, file ) ) != buf_len )
    {
        fclose( file );
        return -1;
    }

    fclose( file );
    return( (int)n );
}

int main()
{
    int ret = 0;
    .
    .
    .
    ret = mbedtls_platform_set_nv_seed( mbedtls_platform_std_nv_seed_read,
                                        mbedtls_platform_std_nv_seed_write );
    if( ret != 0 )
        return -1;

    .
    .
    .
    return( ret );
}
```
# Provisioning your platform with the seed

Every board should have a unique true random seed stored into it at manufacturing time. The seed should be generated offline and then injected into the device at the location of the seed file, where Mbed TLS will look for it. The provisioning of the seed should be done in a secure site, depending on the trust level of your manufacture line.

# Security considerations

There are a few things you need to consider with the NV seed feature, depending on your threat model:

1. As mentioned earlier, the location where the seed is provisioned is dependent on your manufacture line trust level.
1. If your NV memory is vulnerable to offline physical attacks, then your seed file should be stored in a secure encrypted NV memory, only accessible to your application.
1. The seed should be true random and not dependent on any device specific traits, such as the serial number.
1. Every device should be provisioned with a different seed, otherwise, if one device is breached, all the devices provisioned with same seed will be breached as well.
