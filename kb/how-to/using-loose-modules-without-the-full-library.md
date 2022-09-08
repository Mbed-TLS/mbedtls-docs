# Using only a few modules from the library

Mbed TLS is a critical security component. While the developers do their best to avoid bugs and achieve the highest level of security, bugs can happen, including security-critical ones. As a consequence, if you make an application that includes code from Mbed TLS, you should be prepared to upgrade Mbed TLS.

You don't have to use the whole library, however! Mbed TLS is designed so you can include only the modules that you need.

## Making a minimal configuration

The file `include/mbedtls/mbedtls_config.h` contains a list of features and build-time options. To design a minimal configuration, start with a blank file and add the options you need. The documentation of each option describes its dependencies, if any.

Where to put your own configuration file? There are three choices:

* You can edit the file in place, if you wish.
* You can place a file called `mbedtls/mbedtls_config.h` at some location in the include file search path that comes before the `include` directory from the Mbed TLS source tree.
* You can give your configuration file a different name and set the preprocessor symbol `MBEDTLS_CONFIG_FILE` to the location of that file, including surrounding quotes.

For more information, see [How to configure Mbed TLS](../compiling-and-building/how-do-i-configure-mbedtls.md).

### Random generator example

For example, suppose you want a cryptographically secure random generator and nothing else. A random generator consists of two parts: an entropy source, and a pseudorandom generator seeded by the entropy source. Mbed TLS provides an interface to the system's entropy sources in the `entropy` module enabled by `MBEDTLS_ENTROPY_C`. For the pseudorandom generator, there are two choices: CTR\_DRBG or HMAC\_DRBG, enabled with `MBEDTLS_CTR_DRBG_C` and `MBEDTLS_HMAC_DRBG_C` respectively.

The documentation of `MBEDTLS_ENTROPY_C` states that it requires either `MBEDTLS_SHA512_C` or `MBEDTLS_SHA256_C`. The CTR\_DRBG module requires `MBEDTLS_AES_C`. The HMAC\_DRBG module requires `MBEDTLS_MD_C`, which in turn requires at least one hash module.

You decide to use HMAC\_DRBG, and use SHA-512 as the hash function both for entropy and for the DRBG. As a consequence, you write the following configuration file:

```c
#define MBEDTLS_ENTROPY_C
#define MBEDTLS_HMAC_DRBG_C
#define MBEDTLS_MD_C
#define MBEDTLS_SHA512_C
```

### Notes about Mbed TLS 2.x

In Mbed TLS 2.x, the configuration file is located at `include/mbedtls/config.h`.

You should add the following line at the end of your configuration file:
```c
#include "mbedtls/check_config.h"
```
This will cause compilation errors with descriptive messages if the configuration is inconsistent.

## Building Mbed TLS files directly in an application

Mbed TLS comes with build scripts for GNU make (`Makefile`), CMake (`CMakeLists.txt`) and Visual Studio (`visualc/VS2010/mbedTLS.sln`). By default, these create static libraries `mbedcrypto`, `mbedx509` and `mbedtls` which you can link into your application. (You don't need to link `mbedx509` or `mbedtls` if you don't use these features.) For more information, see [How to compile and build Mbed TLS](../compiling-and-building/how-do-i-build-compile-mbedtls.md).

If you prefer, you can include the Mbed TLS source files in your own build scripts. All the library code is in the `library` subdirectory, except for a few features that use code from the `3rdparty` directory tree. All the public headers are in the `include` directory tree.

### Compiling with Mbed TLS headers

Both when building your application and when building Mbed TLS source files, make sure that the `include` directory of the Mbed TLS source tree is present in the header search path. For example, if Mbed TLS is in the subdirectory `external/mbedtls`:
```console
$ cc -I external/mbedtls/include …
```

If you have a custom configuration file with the same name in a different directory, it must come first on the header search path. For example, if your Mbed TLS configuration file is located at `configs/mbedtls/mbedtls_config.h` and the Mbed TLS source tree is located at `external/mbedtls`:
```console
$ cc -I configs -I external/mbedtls/include …
```

Recall that alternatively, you can give your configuration file a different name and specify its location with the preprocessor symbol `MBEDTLS_CONFIG_FILE`. For example, if your Mbed TLS configuration file is located at `my_mbedtls_config.h` and the Mbed TLS source tree is located at `external/mbedtls`.

```console
$ cc -DMBEDTLS_CONFIG_FILE='"my_mbedtls_config.h"' -I configs -I external/mbedtls/include …
```

Note that **you must pass the same configuration when building Mbed TLS and building your application**. Passing a different configuration is likely to result in misbehavior at runtime.

### Linking Mbed TLS objects

When you build Mbed TLS with the provided build scripts, all the source files are compiled. However, the resulting object files are empty for features that are disabled.

If you wish, you can link selectively with just the object files you need. Generally speaking, a feature called `MBEDTLS_XXX_C` is provided by the file `library/xxx.c`. There are a few exceptions:

* The Everest implementation of Curve25519 (`MBEDTLS_ECDH_VARIANT_EVEREST_ENABLED`) requires files from `3rdparty/everest`.
* The PSA cryptography interface (`MBEDTLS_PSA_CRYPTO_C`) requires several files `library/psa_crypto_*.c` in addition to `library/psa_crypto.c` itself.
* The TLS protocol implementation requires `library/ssl_msg.c` and possibly more files `ssl_tls1*.c` depending on which protocol versions are enabled, in addition to `library/ssl_tls.c`.
