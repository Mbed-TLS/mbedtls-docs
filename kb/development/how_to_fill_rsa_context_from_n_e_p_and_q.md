# How to fill an RSA context from N, E, P and Q

## Introduction

In some cases, you only have the base values for RSA at your disposal and want to use those within Mbed TLS. Mbed TLS, specifically the `mbedtls_rsa_context` structure, requires more than the base values to perform optimized operations for RSA.

You can deduce the other values if you have access to your **E**, **P** and **Q**. In most cases, you already have your **N**, so you can skip the next section.

You can import these values to your `mbedtls_rsa_context` structure with their raw value, in Big Endian, using the `mbedtls_rsa_import_raw()` function, or as `mbedtls_mpi` structures, using the `mbedtls_rsa_import()` function.
If you do not wish to set a component to the context, whether you do not know it or it is already set, you can just set it as `NULL` as the function parameter.

The following example shows you how to correctly initialize the RSA context named **ctx** with the values for **P,** **Q** and **E** into `mbedtls_rsa_context`.

## Getting the modulus (N)

If the modulus (**N**) is known, you should send it as parameter to `mbedtls_rsa_import()` (or `mbedtls_rsa_import_raw()`). However if it is not known, it is calculated within the `mbedtls_rsa_complete()` function, if **P** and **Q** have been imported to the context.
    
## Filling the context

To fill the context you should use the following sequence of function calls. You will have to define and initialize the appropriate variables for `E`, `P` and `Q`.

    ret = mbedtls_rsa_import( &ctx, NULL, &P, &Q, NULL, &E );
    if( ret != 0 )
    {
        mbedtls_printf( " failed\n  ! mbedtls_rsa_import returned %d\n\n",
                        ret );
        goto exit;
    }
    if( ( ret = mbedtls_rsa_complete( &ctx ) ) != 0 )
    {
        mbedtls_printf( " failed\n  ! mbedtls_rsa_complete returned %d\n\n",
                        ret );
        goto exit;
    }
    
The function `mbedtls_rsa_complete()` deduces all the other components in the RSA context. Of course, if all components are known in advance and imported using the `mbedtls_rsa_import()` or `mbedtls_rsa_import_raw()`, the computation time of `mbedtls_rsa_complete()` will be shorter.

## Checking the RSA key consistency

If you want to check the correctness of all values in your context, use `mbedtls_rsa_check_privkey()`.
