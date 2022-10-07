# Mbed TLS coding standards

## Intro

This document describes Mbed TLS preferences for code formatting, naming conventions, API conventions, coding style, file structure, and default content.

<span class="notes">**Note:** There are situations where we deviate from this document for 'local' reasons.</span>

## Code Formatting

Mbed TLS source code files use 4 spaces for indentation, **not tabs**, with a preferred maximum line length of 80 characters.

Every code statement should be on its own line.

**Avoid statements like this:**
```c
    if( a == 1 ) { b = 1; do_function( b ); }
    if( a == 1 ) do_function( a );
```

### Space placement

Mbed TLS uses a non-standard space placement throughout the code, where there is no space between a function name and all parentheses are separated by one space from their content:
```c
    if( ( ret = demo_function( a, b, c ) ) != 0 )
```
The same applies to function definitions:
```c
    int demo_function( int a, const unsigned char *value, size_t len )
```
There are a few exceptions to this rule. This includes the preprocessor directive `defined` and casts, as well as arguments for function-like macros:
```c
    #if defined(MBEDTLS_HAVE_TIME)
    timestamp = (uint32_t) time( NULL );
```

### Braces placement and block declaration

Braces (curly brackets) should be located on a line by themselves at the indentation level of the original block:
```c
    if( val >= 1 )
    {
        if( val == 1 )
        {
            /* code block here */
        }
        else
        {
            /* alternate code block */
        }
    }
```
In case a block is only single source code line, the braces can be omitted if the block initiator is only a single line:
```c
    if( val >= 1 )
        a = 2;
```
But not if it is a multi-line initiator:
```c
    if( val >= 1 &&
        this_big_statement_deserved_its_own_line == another_big_part )
    {
        a = 2;
    }
```

### Related lines: Multi-line formatting and indentation

Multiple related source code lines should be formatted to be easily readable:
```c
#define GET_UINT32_LE( n, b, i )                        \
{                                                       \
    (n) = ( (uint32_t) (b)[(i)    ]       )             \
        | ( (uint32_t) (b)[(i) + 1] <<  8 )             \
        | ( (uint32_t) (b)[(i) + 2] << 16 )             \
        | ( (uint32_t) (b)[(i) + 3] << 24 );            \
}

if( my_super_var == second_super_var &&
    this_check_will_do != the_other_value )

do_function( ctx, this_is_a_value, value_b,
                  the_special_var );

void this_is_a_function( context_struct *ctx, size_t length,
                         unsigned char *result );
```

### Extra parentheses for `return` and `sizeof`

Within Mbed TLS return statements use parentheses to contain their value:
```c
    return( 0 );
```
Similarly, sizeof expressions always use parentheses even when it is not necessary (when taking the size of an object):
```c
    memset( buf, 0, sizeof( buf ) );
```

### Preprocessor directives

When using preprocessor directives to enable or disable parts of the code, use `#if defined` instead of `#ifdef`. Add a comment to the `#endif` directive if the distance to the opening directive is bigger than a few lines or contains other directives:
```c
    #if define(MBEDTLS_HAVE_FEATURE)
    /* ten lines of code or other directives */
    #endif /* MBEDTLS_HAVE_FEATURE */
```

## Naming conventions

### Name spacing

All public names (functions, variables, types, `enum` constants, macros) must start with either `MBEDTLS_` or `mbedtls_`, usually followed by the name of the module they belong to (and submodule if applicable), followed by a descriptive part. Macros and `enum` constants are uppercase with underscores; other names are lowercase with underscores:
```c
    mbedtls_x509_crt_parse_file()
    mbedtls_aes_setkey_decrypt()
```

Note that all externally linked functions must have a name starting with `mbedtls_` to avoid link-time conflicts, even if they are not declared in a public header. This also applies to global variables (which should be used very sparingly).

Exception: code implementing the PSA crypto API uses the `PSA_` and `psa_` prefixes. This includes official APIs as well as draft APIs that are on the PSA standards track. API extensions which are meant to remain specific to Mbed TLS, and internal functions, should use the `MBEDTLS_/mbedtls_` prefix, however there are many existing cases of using the `PSA_/psa_` prefix.

Exception: macros may have lowercase names if they behave exactly like normal variables and functions. In particular, function-like macros may have lowercase names only if they expand to an expression that evaluates each argument exactly once. Even in those cases, uppercase names are strongly preferred and new code should not use lowercase macro names for anything other than function replacement (like `#define mbedtls_printf printf`).

### Local names

Static functions can use the same naming scheme as non-static functions (`mbedtls_MODULE_frobnicate()` or `psa_frobnicate()`). This is convenient if they are made non-static later, for example for testing. They can also have shorter names if it's convenient. Keeping the module name (`MODULE_frobnicate()`) as a prefix makes it slightly easier to follow call stacks across modules, but it is not compulsory.

Macros defined only in the `library` directory should follow the same naming scheme as non-static functions (`MBEDTLS_MODULE_FOO` or `PSA_FOO`). They can use shorter names (omitting `MBEDTLS_`, the module name, or both) if it's convenient. However, avoid names without underscores as some embedded platforms define short macro names in their system headers. Exception: macros defined in headers used by alternative implementations or PSA drivers (including headers that they include) must start with `MBEDTLS_` or `PSA_`.

Function parameters and local variables need no name spacing. They should use descriptive names unless they're very short-lived or are used for simple looping or are "standard" names (such as `p` for a pointer to the current position in a buffer).

### Lengths and sizes

By default all lengths and sizes are in bytes (or in number of elements, for arrays). If a name refers to a length or size in bits (as is often the case for key sizes) then the name must explicitly include `bit`, for example `mbedtls_pk_get_bitlen()` returns the size of the key in bits, while `mbedtls_pk_get_len()` returns the size in bytes. In addition, the documentation should always mention explicitly if key sizes are in bits or in bytes.

`size` should refer to the capacity of a buffer, and `length` to the length of the contents. Most of the time these are interchangeable. A typical exception is when the output is written in a buffer, but the exact length is not known by the caller.

### Modules: `bignum_core`, `bignum_mod` and `bignum_mod_raw`

Generic conventions:

- `mbedtls_mpi_uint *` input operands should be named by capital letters starting at the beginning of the alphabet (`A`, `B`, `C`, ...).
- `mbedtls_mpi_uint` operands in turn should be named by lower case letters starting at the beginning of the alphabet (`a`, `b`, `c`)
- For the result `X` or `x` should be used depending on the type.
- `N` is generally used for the modulus.
- `T` is generally used for a temporary work area given to a function.
- An exception from this convention is where the naming of function parameters and local variables follows the literature (e.g. Handbook of Applied Cryptography)

Length parameters:

- For length of `mbedtls_mpi_uint *` buffers we use `limbs`.
- Length parameters are qualified if possible (e.g. `input_length` or `A_limbs`)

## API conventions

This section applies fully to classic `mbedtls_xxx()` APIs and mostly to the newer `psa_xxx()` APIs. PSA have their own [conventions described in the PSA Crypto API specification](https://armmbed.github.io/mbed-crypto/html/overview/conventions.html) which take precedence in case of conflicts.

### Module contexts

If a module uses a context structure for passing around its state, the module should contain an `init()` and `free()` function, with the module or context name prepended to it. The `init()` function must always return `void`. If some initialization must be done that may fail (such as allocating memory), it should be done in a separate function, usually called `setup()`. The `free()` function must free any allocated memory within the context, but not the context itself. It must set to zero any data in the context or substructures:
```c
    mbedtls_cipher_context_t ctx;
    mbedtls_cipher_init( &ctx );
    ret = mbedtls_cipher_setup( &ctx, ... );
    /* Check ret, goto cleanup on error */
    /* Do things, goto cleanup on error */
    cleanup:
    mbedtls_cipher_free( &ctx );
```
The goal of separating the `init()` and `setup()` part is that if you have multiple contexts, you can call all the `init()` functions first and then all contexts are ready to be passed to the `free()` function in case an error happens in one of the `setup()` functions or elsewhere.

### Return type

Most functions should return `int`, more specifically `0` on success (the operation was successfully performed, the object checked was found acceptable, etc.) and a negative error code otherwise. Each module defines its own error codes, see `error.h` for the allocation scheme. Exceptions to this rule:

* Functions that can never fail should either return `void` (such as `mbedtls_cipher_init()`) or directly the information requested (such as `mbedtls_mpi_get_bit()`).
* Functions that look up some information should return either a pointer to this information or `NULL` if it wasn't found.
* PSA functions that can fail return a [`psa_status_t` value](https://armmbed.github.io/mbed-crypto/html/overview/conventions.html#return-status).
* Some functions may multiplex the return value, such as `mbedtls_asn1_write_len()` returns the length written on success or a negative error code. This mimics the behavior of some standard functions such as `write()` and `read()`, except there is no equivalent to `errno`: the return code should be specific enough.
* Some internal functions may return `-1` on errors rather than a specific error code; it is then up to the calling function to pick a more appropriate error code if the error is to be propagated back to the user.
* Functions whose name clearly indicates a boolean (such as, the name contains "has", "is" or "can") should return `0` for false and `1` for true. The name must be clear: for example, `mbdtls_has_foobar_support()` will return `1` if support for foobar is present; by contrast, `mbedtls_check_foobar_support()` will return `0` if support for foobar is present (success) and `-1` or a more specific error code if not. All functions named `check` must follow this rule and return `0` to indicate acceptable/valid/present/etc. Preference should generally be given to `check` names in order to avoid a mixture of `== 0` and `!= 0` tests.
* Functions called `cmp` must return `0` if the two arguments are equal, and if it makes sense, should return `-1` or `1` to indicate which argument is greater.

### Limited use of in-out parameters

Function should avoid in-out parameters for length (multiplexing buffer size on entry with length used/written on exit) since they tend to impair readability. For example:
```c
    mbedtls_write_thing( void *thing, unsigned char *buf, size_t *len ); // no
    mbedtls_write_thing( void *thing, unsigned char *buf, size_t buflen,
                         size_t *outlen ); // yes
```

For PSA functions, [input buffers](https://armmbed.github.io/mbed-crypto/html/overview/conventions.html#input-buffer-sizes) have a `size_t xxx_size` parameter after the buffer pointer, and [output buffers](https://armmbed.github.io/mbed-crypto/html/overview/conventions.html#output-buffer-sizes) have a `size_t xxx_size` parameter for the buffer size followed by a `size_t *xxx_length` parameter for the output length. This convention is also preferred in new `mbedtls_xxx` code, but older modules often use different conventions.

You can use in-out parameters for functions that receive a pointer to some buffer, and update it after parsing from or writing to that buffer:
```c
    mbedtls_asn1_get_int( unsigned char **p,
                          const unsigned char *end,
                          int *value );
```
In that case, the `end` argument should always point to one past the one of the buffer on entry.

Also, contexts are usually in-out parameters, which is acceptable.

### `Const` correctness

Function declarations should keep `const` correctness in mind when declaring function arguments. Arguments that are pointers and are *not* changed by the functions should be marked as such:
```c
    int do_calc_length( const unsigned char *str )
```

## Coding style

### ISO C99

The code uses the C99 ISO standard.

### Proper argument and variable typing

Type function arguments and variables properly. Specifically, the `int` and `size` fields hold their maximum length in a platform-independent way. For buffer length, this almost always means using `size_t`.

For values that can't be negative, use unsigned variables. Keep the type in mind when building loops with unsigned variables.

### `Goto`

Use of `goto` is allowed in functions that have to do cleaning up before returning from the function even when an error has occurred. It can also be used to exit nested loops. In other cases the use of `goto` should be avoided.

### Exit early and prevent nesting

Structure functions to exit or `goto` the exit code as early as possible. This prevents nesting of code blocks and improves code readability.

Most functions that need cleanup have a single cleanup block at the end. The label for this block can be `cleanup:` or `exit:` (or `error:` if the block is skipped on success); follow the established convention when extending an existing module. Code that uses bignum must use `cleanup:` for the sake of `MBEDTLS_MPI_CHK`.

### External function dependencies

Mbed TLS code should minimize use of external functions. Standard `libc` functions are allowed, but should be documented in the [KB article on external dependencies](what-external-dependencies-does-mbedtls-rely-on.md).

### Minimize code based on preprocessor directives

To minimize the code size and external dependencies, the availability of modules and module functionality is controlled by preprocessor directives located in `mbedtls/mbedtls_config.h`. Each module should have at least its own module define for enabling or disabling the module altogether. Other files using the module header should only include the header file if the module is actually available.

Since often systems that use Mbed TLS do not have a file system, functions specifically using the file system should be contained in `MBEDTLS_FS_IO` directives.

### Minimize use of macros

Avoid using macros unless:
* Readability actually improves with use of the macro.
* Code size is drastically impacted.

The following define actually makes the code using it easier to read.
```c
#define GET_UINT32_LE( n, b, i )                        \
{                                                       \
    (n) = ( (uint32_t) (b)[(i)    ]       )             \
        | ( (uint32_t) (b)[(i) + 1] <<  8 )             \
        | ( (uint32_t) (b)[(i) + 2] << 16 )             \
        | ( (uint32_t) (b)[(i) + 3] << 24 );            \
}
```

## Clear security-relevant memory after use

Memory that contains security-relevant information should be set to zero after use, and before being released to be reused. Use the function `mbedtls_platform_zeroize()` to prevent unwanted compiler optimization.

## Clear and free what you made

The module that allocated a piece of heap memory is also responsible for releasing it later on unless explicitly documented in the function definition in the header file.

## `Module self_test()`

Each module should have a self-test function (between a check for **MBEDTLS_SELF_TEST**). This function should test basic module sanity, but stay away from performing time-consuming tests.

## Doxygen documentation formatting

The header files should be documented with Doxygen-style code comments. Use the **'\'** character as a separator.

|Function|Description|
|---|---|
|\brief|A useless function present for documentation purposes.|
|\note|This function has no influence on code security.|
|\param buf|Buffer to ignore.|
|\param len|Length of buffer.|
|\return|0 if successfully ignored, otherwise, a module-specific error code.|

## Loose coupling interfaces

Each module should keep loose coupling with external modules and functions in mind. Use flexible function pointers over hard functions calls in cases where you want to replace part of the code with a local version.

## Generic file structure

### Header files

Structure header files as follows:

* Brief description of the file.
* Copyright notice and license indication.
* Header file define for `MBEDTLS_ {MODULE_NAME} _H`:
```c
#ifndef MBEDTLS_AES_H
#define MBEDTLS_AES_H
```
* Includes. Always include `<mbedtls/build_info.h>` before anything that might depend on the compile-time configuration.
* Public defines (Generic and error codes) and portability code.
* C++ wrapper for C code:
```c
#ifdef __cplusplus
extern "C" {
#endif
```
* For modules with optional alternative implementations, check for module specific structures:
```c
#if !defined(MBEDTLS_AES_ALT)
```
* Public structures that can have alternative implementations.
* For modules with optional alternative implementations, include the alternative header file:
```c
#else  /* MBEDTLS_AES_ALT */
#include "aes_alt.h"
#endif /* MBEDTLS_AES_ALT */
```
* Public structures that should not have alternative implementations.
* Function declarations.
* C++ end wrapper:
```c
#ifdef __cplusplus
}
#endif
```
* Header file end define:
```c
#endif /* MBEDTLS_AES_H */
```

### Source files

Source files are structured as follows:

* Brief description of the file.
* Copyright notice and license indication.
* Comments on possible standard documents used.
* Preprocessor directive for module:
```c
#if defined(MBEDTLS_AES_C)
```
* Includes. All library source files start by including `"common.h"`.
* If applicable, preprocessor directive for alternative implementation:
```c
#if !defined(MBEDTLS_AES_ALT)
```
* Private local defines and portability code.
* Function definitions.
* If applicable, preprocessor directive for marking the end of an alternative implementation:
```c
#endif /* !MBEDTLS_AES_ALT */
```
* Preprocessor directive for selftest (where applicable):
```c
#if defined(MBEDTLS_SELF_TEST)
```
* Self-test test vectors.
* Self test implementation.
* Preprocessor directive for marking the end of self tests (where applicable):
```c
#endif /* MBEDTLS_SELF_TEST */
```
* Preprocessor directive for marking the end of a module:
```c
#endif /* MBEDTLS_AES_C */
```

<!---mbedtls-coding-standards
,"Coding standards used in the Mbed TLS code, include default code formatting, coding style and file structures.","code formatting, coding style, file structures, code standards","code, formatting, style, coding style",published,"2012-10-18 11:34:00",3,7553,"2017-06-05 11:14:00","Paul Bakker"--->
