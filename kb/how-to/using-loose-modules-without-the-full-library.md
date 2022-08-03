# Using loose modules without the full library

## Separate application

If you want to make an application by using parts or modules of Mbed TLS, rather than building and including the entire Mbed TLS library, then rest assured.  Mbed TLS was made for this.


## Simple random number generator

In the example below, we make an application called `rng` that generates random data. The application needs the `CTR_DRBG` module, which depends on the `Entropy` module, the `SHA-512` module and the `AES` module.

To make the application, follow these steps:

* Make a directory structure to work in.
* Copy the relevant Mbed TLS files to the correct location.
* Write a `Makefile`.
* Write a `config.h` file for Mbed TLS.
* Write the `rng.c` source file for the application.
* Make the application.
* Run the application that generates random data.

## 1. The directory
Make a directory structure as follows:

```
my_dir/
  mbedtls/
```

## 2. The Mbed TLS files

Copy the following files from the Mbed TLS source directory `library/` to `my_dir/`:

* `aes.c`
* `entropy.c`
* `entropy_poll.c`
* `mbedtls_sha512.c`
* `ctr_drbg.c`

In addition, copy the following files from the Mbed TLS include directory `include/mbedtls/` to `my_dir/mbedtls/`:

* `aes.h`
* `entropy.h`
* `entropy_poll.h`
* `mbedtls_sha512.h`
* `ctr_drbg.h`

## 3. The Makefile

Because we are using Linux, we will write a very straightforward `Makefile` to build the application in `my_dir/Makefile`:

```
CFLAGS  += -I. -D_FILE_OFFSET_BITS=64 -Wall -W -Wdeclaration-after-statement
OFLAGS  = -O2

OBJS=   entropy.o       entropy_poll.o  ctr_drbg.o      mbedtls_sha512.o        aes.o

all: rng

.SILENT:

.c.o:
        echo "  CC    $<"
        $(CC) $(CFLAGS) $(OFLAGS) -c $<

rng: rng.c $(OBJS)
        echo   "  CC    rng"
        $(CC) $(CFLAGS) $(OFLAGS) rng.c -o $@ $(OBJS)

clean:
    rm -f *.o rng
```

## 4. The configuration: config.h

We need to tell the Mbed TLS modules which parts they should activate during compilation. To enable compilation of the actual modules, Mbed TLS uses a configuration file, which should also be located in `mbedtls/`. We only want to activate basic functionality in our example application, so use the following file for `mbedtls/config.h`:

```
#define MBEDTLS_AES_C
#define MBEDTLS_ENTROPY_C
#define MBEDTLS_CTR_DRBG_C
#define MBEDTLS_SHA512_C
```

This ensures that the content compiles.

## 5. The Application: rng.c

Write a `rng.c` source file for the application. This application generates 1024 bytes of random and writes them to `output.rnd`:

```
/**
 *  \brief Simple RNG generation example
 */

#include "mbedtls/config.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/check_config.h"

#include <stdio.h>

int main( void )
{
    FILE *f;
    int ret;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_entropy_context entropy;
    unsigned char buf[1024];

    if( ( f = fopen( "output.rnd", "wb+" ) ) == NULL )
    {
        printf( "failed to open 'output.rnd' for writing.\n" );
        return( 1 );
    }

    mbedtls_entropy_init( &entropy );
    if( ( ret = mbedtls_ctr_drbg_init( &ctr_drbg, mbedtls_entropy_func, &entropy,
                               (const unsigned char *) "RANDOM_GEN",
                               10 ) ) != 0 )
    {
        printf( "failed in ctr_drbg_init\n");
        goto cleanup;
    }

    if( ( ret = mbedtls_ctr_drbg_random( &ctr_drbg, buf, sizeof( buf ) ) ) != 0 )
    {
        printf("failed in ctr_drbg_random!\n");
        goto cleanup;
    }

    fwrite( buf, 1, sizeof( buf ), f );

    ret = 0;
    printf("Random generated in 'output.rng'\n");

cleanup:
    fclose( f );
    mbedtls_entropy_free( &entropy );

    return( ret );
}
```

### Final directory content
The file structure should now look like this:

```
my_dir/
  aes.c
  ctr_drbg.c
  entropy.c
  entropy_poll.c
  Makefile
  mbedtls/
    aes.h
    config.h
    ctr_drbg.h
    entropy.h
    entropy_poll.h
    mbedtls_sha512.h
  rng.c
  mbedtls_sha512.c
```

## 6. Make the application

To make the application, type `make` in the `my_dir/` directory:

```
$ make
  CC    entropy.c
  CC    entropy_poll.c
  CC    ctr_drbg.c
  CC    mbedtls_sha512.c
  CC    aes.c
  CC    rng
$
```

## Run the application that generates random data

Now, run the `rng` application to generate random data:

```
$ ./rng
Random generated in 'output.rnd'
$
```


<!--",using-loose-modules-without-the-full-library,"Step-by-step guide on how to make an application with loose modules from Mbed TLS without including or building the entire library",,"modules, example, tutorial, random",published,"2014-03-28 10:58:00",2,4038,"2015-07-24 09:51:00","Paul Bakker"-->
