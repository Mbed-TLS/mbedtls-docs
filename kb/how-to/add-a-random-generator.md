<h1 id="random-data">Random data generation</h1>

When making a security application, you may require a random data generator. Arm Mbed TLS includes the [CTR-DRBG module](ctr-drbg-source-code.html) for random generation.

Setting up CTR-DRBG in your code requires an entropy source and a personalization string.

## Setting up the entropy source

Mbed TLS includes the [entropy collection module](entropy-source-code.html) to provide a central pool of entropy from which to extract entropy.

To use the entropy collector in your code, include the header file:

```
#include "mbedtls/entropy.h"
```

Add the following somewhere in your `main()`:

```c
    mbedtls_entropy_context entropy;
    mbedtls_entropy_init( &entropy );
```

If your platform has a hardware TRNG or PRNG in the processor or TPM, you can hook it up to the entropy collector with `entropy_add_source()` to enhance the entropy even further. Please see our article on [how to add an entropy source to the entropy pool](add-entropy-sources-to-entropy-pool.html) for more information.

## The random generator

To use the CTR-DRBG module in your code, you need to include the header file:

```c
#include "mbedtls/ctr_drbg.h"
```

Add:

```c
    mbedtls_ctr_drbg_context ctr_drbg;
    char *personalization = "my_app_specific_string";

    mbedtls_ctr_drbg_init( &ctr_drbg );

    ret = mbedtls_ctr_drbg_seed( &ctr_drbg , mbedtls_entropy_func, &entropy,
                     (const unsigned char *) personalization,
                     strlen( personalization ) );
    if( ret != 0 )
    {
        // ERROR HANDLING CODE FOR YOUR APP
    }
```

The **personalization** string is a small protection against a lack of startup entropy and ensures each application has at least a different starting point.

## Enabling prediction resistance

To prevent an adversary from reading your random data, you can enable prediction resistance:

```c
mbedtls_ctr_drbg_set_prediction_resistance( &ctr_drbg, MBEDTLS_CTR_DRBG_PR_ON );
```

<span class="notes">**Note:** If enabled, entropy is gathered before each call. Only use this if you have ample supply of good entropy.</span>

## Loading a seed file

Another way to add entropy at the start of your application is to use a seed file. The Mbed TLS random generator can read and update a seed file with `mbedtls_ctr_drbg_update_seed_file()` to increase entropy.

## Multithreaded use

If you intend to use the CTR-DRBG module in multiple threads, please read our article on [entropy collection, random generation with threads](/kb/development/entropy-collection-and-random-generation-in-threaded-environment).

<!--- "add-a-random-generator","Short article on how to add a good random generator to your application. Complete with source code examples!",,"entropy, random data, random number generator, RNG, ctr-drbg, entropy pool, security",published,"2013-09-11 12:10:00",2,11128,"2017-04-24 11:16:00","Paul Bakker" --->
