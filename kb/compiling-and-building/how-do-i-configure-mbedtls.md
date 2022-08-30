# How to configure Mbed TLS

Mbed TLS should build out-of-the box on a large variety of platforms. However, you may need to adjust a few platform-specific settings or want to customize the set of features that will be built. You can do all of this in a single configuration file.

## The configuration file

The default configuration file is located in `include/mbedtls/mbedtls_config.h` (`include/mbedtls/config.h` up to Mbed TLS 2.28). It is [fully documented](/api/config_8h.html) and contains the following sections:

* Select options depending on your platform in **System support**: does your compiler support inline assembly, does your libc/network stack provide IPv6, and so on.
* Select which features you want to enable for corresponding modules in **Mbed TLS feature support**: which TLS version to support, which key exchanges, which specific elliptic curves, and so on.
* Select modules to build in **Mbed TLS modules**. You can, for example, completely disable RSA or MD5 if you don't need them.
* Set specific options for each module, such as the maximum size of multi-precision integers, or the size of the internal I/O buffers for SSL, in **Module configuration options**. All of these options have default values.

## The configuration script

You can edit the configuration file manually with a text editor of your choice. In some cases, however, it may be useful to set options in a more programmatic way. We provide a Perl script `scripts/config.pl` for doing so:
    ```
    scripts/config.pl unset <name>
    scripts/config.pl set <name> [<value>]
    ```
The `config.pl` script automatically finds the `mbedtls_config.h` file when it runs this way from Mbed TLS' root directory. If you want to run it from another directory or on another configuration file (see below), you need to use the `-f` option.

## Alternative configuration files

You might want to keep the custom configuration file for your application outside the Mbed TLS source tree. You can do this by defining the macro `MBEDTLS_CONFIG_FILE` for the desired filename (including the quote or angular brackets) at compile time. For example, using **make**:
    ```
     CFLAGS="-Ipath/to/config -DMBEDTLS_CONFIG_FILE='<my_config.h>'" make
    ```
or, using **Cmake**:

* If it is not the first run, **clear its cache** before running:
    ```
    find . -iname '*cmake*' -not -name CMakeLists.txt -exec rm -rf {} +
    CFLAGS="-Ipath/to/config -DMBEDTLS_CONFIG_FILE='<my_config.h>'" cmake .
    make
    ```
**Mbed TLS 2.2x only:** We provide a `check_config.h` file that checks the consistency of the configuration file. We highly recommended to `include` it at the end of your custom configuration file. If you use the above setup, you may need to adapt the `include` directive depending on your compiler. (Since Mbed TLS 3.0, `check_config.h` is included automatically.)

## Example configurations

We provide example configurations in the `configs` directory. These are often minimal configurations for a specific goal, such as supporting the `NSA suite B TLS` profile. They also often include settings to [reduce resource usage](/kb/how-to/reduce-polarssl-memory-and-storage-footprint.md).

<!---",how-do-i-configure-mbedtls,"Short article on configuring Mbed TLS before compilation.",,"configuration, compiling",published,"2014-11-14 12:40:00",6,21074,"2015-07-24 11:53:00","Manuel PÃ©gouriÃ©-Gonnard"--->
