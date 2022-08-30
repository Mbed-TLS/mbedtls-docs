# Alternative cryptography engines implementation

As mentioned in the [Mbed TLS Abstraction layers article](../generic/abstraction-layers.md), Mbed TLS supports alternative implementation for most of its cryptography modules. A common use case is for hardware accelerated cryptography engines. There are a couple of methods for alternative implementations: specific function replacement and full module replacement. The latter is the more common one.

The [configuration file (`mbedtls_config.h`)](https://github.com/Mbed-TLS/mbedtls/blob/development/include/mbedtls/mbedtls_config.h) lists the cryptography modules, which you can replace with alternative implementation. An alternative implementation of a module is effectively a driver for a piece of cryptographic hardware. These are named `MBEDTLS_<MODULE NAME>_ALT`. In order to support an alternative implementation for a module, uncomment the corresponding `*_ALT` definition. Function replacement is based on the function name, upper-cased, with the suffix `_ALT`. To support a hardware entropy source, enable `MBEDTLS_ENTROPY_HARDWARE_ALT` in the configuration file.  

**Note: For RSA and ECP function replacement, the behavior is different. Refer to the [ECP internal header](https://github.com/Mbed-TLS/mbedtls/blob/development/library/ecp_internal_alt.h) for more information.**  

Note: for more information about the configuration file, see [How do I configure Mbed TLS](../compiling-and-building/how-do-i-configure-mbedtls.md).

Some hardware acceleration engines require an initial setup to be done on the platform, before they can work, such as enabling cache, or initializing the cryptographic engine. Such setup should be implemented in the function `mbedtls_platform_setup()` and terminated in the function `mbedtls_platform_teardown()`, as shown in the example in [this article](../how-to/how-do-i-port-mbed-tls-to-a-new-environment-OS.md).

## Guidelines

There are few basic rules for supporting full module alternative implementation:  
1. Enable the relevant `*_ALT` in the configuration file.  
1. Define the module context in `<module name>_alt.h` file.  
1. Implement the module API in `<module name>_alt.c` file.  
1. If the hardware doesn't support specific functionality, such as key size, then the developer must decide whether to implement a software fallback or return the error `MBEDTLS_ERR_PLATFORM_FEATURE_UNSUPPORTED`.

- For "function alternative implementation" method, implement the alternative function in any file that is being compiled as part of the library.  
- For hardware entropy implementation, implement `mbedtls_hardware_poll()` in any file that is being compiled as part of the library.

<span class="notes">**Note:** In the case of unsupported features, we recommend you return the error `MBEDTLS_ERR_PLATFORM_FEATURE_UNSUPPORTED` instead of falling back to software implementation because:

-  Adding software fallback for features not supported by your hardware accelerator doesn't reduce code size, so your users miss out on this advantage of using a hardware accelerator.
- Copying the software implementation from Mbed TLS will require updating your ALT implementation every time Mbed TLS updates in order to get bug fixes and other enhancements.</span>

## Full module replacement example: AES

In `mbedtls_config.h`:

- **Enable** the definition of `MBEDTLS_AES_ALT`.

Create a file `aes_alt.h`:

- **Define** `mbedtls_aes_context` that will fit the platform's needs.
- **Define** the platform specific functions that will be used by the alternative implementation.

Add a file (conventionally `aes_alt.c`) to your build:

-  **Write** an alternative implementation of the AES interface, as defined in `aes.h`, which will access the platform's hardware accelerated engine.

## Function replacement: SHA-256 process

In `mbedtls_config.h`:

- **Enable** the definition of `MBEDTLS_SHA256_PROCESS_ALT`.

Add a file (conventionally `sha256_alt.c`) to your build:

- **Implement** `mbedtls_internal_sha256_process`.
- Mbed TLS 2.x only: Implement `mbedtls_sha256_process` if you need it in legacy applications.
