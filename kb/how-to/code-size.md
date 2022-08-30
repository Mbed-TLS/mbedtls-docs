# How to get code size of the library

Embedded platforms have memory limitations. Deciding what library to use on your product is important, to save overall code size. Therefore, you need the code size of Mbed TLS. This article is relevant for platforms running on Cortex M3/M4.

Mbed TLS is a configurable library, so its code size varies, depending on the configuration used. For more information on how to control and reduce the code size, see [Reducing Mbed TLS memory and storage footprint](reduce-polarssl-memory-and-storage-footprint.md).

Obtain the code size of the library by using the `arm-none-eabi-size -t` command (when using the `arm-none-eabi` toolchain).

Mbed TLS supplies a script that checks the [footprint](https://github.com/ARMmbed/mbedtls/blob/development/scripts/footprint.sh) of the library. The script shows the code size of the library compiled with several configuration files:

* `include/mbedtls/mbedtls_config.h` (`include/mbedtls/config.h` in Mbed TLS 2.x) - The default configuration file, unless modified by the user.
* `configs/config-thread.h` - A minimal configuration example of Mbed TLS using Thread networking protocol.
* `configs/config-suite-b.h` - A minimal configuration example supporting NSA Suite B.
* `configs/config-ccm-psk-tls1_2.h` - A minimal configuration example supporting preshared key and with AES-CCM.

## Prerequisites

* `arm-none-eabi` toolchain installed and found in the `PATH` environment variable.
* `make`.
* POSIX shell.
* Updated `include/mbedtls/mbedtls_config.h` with the required configuration. See [How do I configure Mbed TLS](/kb/compiling-and-building/how-do-i-configure-mbedtls.md) for more information.

Note: The `arm-none-eabi` toolchain may give different results than other toolchains, such as `ARMCC` or `IAR.

## Usage

    ./scripts/footprint.sh

Output will be:
>     Footprint of standard configurations (minus net_sockets.c, timing.c, fs_io)
>     for bare-metal ARM Cortex-M3/M4 microcontrollers.
>
>     Mbed TLS 2.4.1 (git head: af610a0baf)
>     arm-none-eabi-gcc (15:4.9.3+svn231177-1) 4.9.3 20150529 (prerelease)
>     CFLAGS=-Os -march=armv7-m -mthumb
>
>     default (include/mbedtls/config.h):
>        text	   data	bss	dec	hex	filename
>      250087	612	   9360	 260059	  3f7db	(TOTALS)
>
>     thread (configs/config-thread.h):
>        text	   data	bss	dec	hex	filename
>       58021	 19	 10	  58050	   e2c2	(TOTALS)
>
>     suite-b (configs/config-suite-b.h):
>        text	   data	bss	dec	hex	filename
>       79988	 88	 11	  80087	  138d7	(TOTALS)
>
>     psk (configs/config-ccm-psk-tls1_2.h):
>        text	   data	bss	dec	hex	filename
>       28115	 12	  4	  28131	   6de3	(TOTALS)

When you use Mbed TLS as a static library, you can optimize the linker to omit any unused symbol. You can find full symbol information in `mbedtls-footprint.zip`.
