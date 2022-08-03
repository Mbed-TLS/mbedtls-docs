# How to define error codes for new modules

## How error codes are structured

The main structure for the error codes is documented in the `error.h` file.

Currently, we try to keep all error codes within the negative space of 16 bit signed integers to support all 16-bit and 32-bit platforms (-0x0001 - -0x7FFF). In addition we'd like to give two layers of information on the error if possible. For example, if an X.509 certificate is not parsed correctly because of an ASN.1 error, we would like to reflect that in the error code.

For that purpose we have divided the different modules into high-level and low-level modules. The low-level modules don't depend massively on anything else, such as the ASN.1 parser, the AES module, the SHA1 module or the OID database. The high-level modules are the ones that use low-level modules a lot, such as the X.509 parser, the RSA module or the main SSL module.

For that purpose the 16-bit error codes are segmented in the following manner:

- 1 bit Unused (sign bit)
- 3 bits High level module ID
- 5 bits Module-dependent error code
- 7 bits Low level module errors

For historical reasons, low-level error codes are divided in even and odd, even codes were assigned first, and -1 is reserved for other errors.

This space-division allows one error code to propagate one low-level error and one high-level error in the same error code by just adding them together (`HIGH_LEVEL_ERROR + LOW_LEVEL_ERROR`).

<span class="notes">**Note:**: As the error codes are negative and processors use 2's complement internally for representing negative numbers, XOR'ing them together does not work.</span>

As error codes are something 'internal', the actual representation and division is not relevant for high-level users that will only use the defined values anyway.

## Adding a new low-level module to Mbed TLS

Find some space within the `error.h` file to fit the number of the error codes you need.

Add the name to the list of low-level modules in the `error.h` file and in `scripts/generate_errors.pl`.

## Adding a new high-level module to Mbed TLS

Find some module space in the `error.h` file to fit the number of error codes you need. As all the high-level module numbers are filled, we are now also starting to use the same numbers from the top.

Add the name to the list of high-level modules in the `error.h` file and in `scripts/generate_errors.pl`.

## User-friendly error strings for `mbedtls_strerror()`

Add the respective error codes to your module's header file with a description, like this:

```
#define MBEDTLS_ERR_AES_INVALID_KEY_LENGTH-0x0020  /**< Invalid key length. */
```

The doxygen description will be used as the user-friendly `mbedtls_strerror()` error message.

Regenerate the `error.c` file.

Now regenerate `library/error.c` with:

`scripts/generate_errors.pl`
