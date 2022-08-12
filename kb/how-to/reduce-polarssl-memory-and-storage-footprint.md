# Reducing Mbed TLS memory and storage footprint

This page includes some of the optimizations that can help you reduce the RAM and ROM footprint of the Mbed TLS library. These are generic optimizations that do not require massive modifications to the code. This page discusses reductions of the compiled library (see [Binary footprint](#binary-footprint)) and reductions to the runtime memory (see [Memory footprint](#memory-footprint)).

All of the settings described on this page are available in `config.h`, see [How do I configure Mbed TLS](../compiling-and-building/how-do-i-configure-mbedtls.md).

If you need to reduce your memory footprint even more or have related questions, please submit a query in our [support forum](https://forums.mbed.com/c/mbed-tls.html) or open an issue in our [GitHub repository](https://github.com/ARMmbed/mbedtls/issues.html). We welcome ideas you may have to further reduce the size in RAM or ROM storage. Please, let us know if you have suggestions for improvements.

# Binary footprint

The binary footprint is the size of the actual file on disk, in the ROM or the flash.

## Minimizing features

By default, Mbed TLS offers several compatibility options and frequently used functionalities. To reduce the footprint, adapt `config.h` to disable the functions that you do not need.

# Memory footprint

The memory footprint is the size of the memory needed at runtime to store variables, contexts and other runtime information.

## Multiple Precision Integers (MPIs)

### Reducing the maximum size of MPIs

By default, `MBEDTLS_MPI_MAX_SIZE` is set to 1024 bytes (8192 bits). If you know that you will not use larger MPIs, you can reduce `MBEDTLS_MPI_MAX_SIZE`.

### Reducing the MPI window size

By default, `mbedtls_mpi_exp_mod()` uses a sliding window size (`MBEDTLS_MPI_WINDOW_SIZE`) of up to 6. You can reduce this value down to 1, which reduces the memory used to the detriment of performance. This only has an effect if you use RSA, DHM or `mbedtls_mpi_exp_mod()` directly.

## Elliptic curves

### Disabling unused ECP curves

Disabling large elliptic curves that you do not use in your application saves a lot of memory.

### Reducing the maximum ECP bits

By default, the `MBEDTLS_ECP_MAX_BITS` is set to `521` to support 521 bits elliptic curves. If you know that you will only use smaller curves, you can safely reduce this value. However, this only has a minimal effect on the memory used.

### Reducing the ECP window size

By default, elliptic curve multiplications use a window size (`MBEDTLS_ECP_WINDOW_SIZE`) of up to 6. You can reduce this value down to 2, which reduces the memory used to the detriment of performance. The larger the elliptic curves, the bigger the impact. See also [How to tune ECC resource usage](/kb/how-to/how-do-i-tune-elliptic-curves-resource-usage.md).

### Disabling the ECP fixed point optimizations

If you disable the ECP fixed point optimizations (`MBEDTLS_ECP_FIXED_POINT_OPTIM`), you lose some performance but use less memory. See also [How to tune ECC resource usage](/kb/how-to/how-do-i-tune-elliptic-curves-resource-usage.md).

## SSL/TLS

### Reducing the SSL frame buffer

By default, Mbed TLS uses a 16 KB frame buffer to hold data for incoming and outgoing frames. This is a TLS standard requirement. If you control both sides of a connection (server and client), you can reduce the maximum frame size to reduce the buffers needed to store the data. The size of this frame is determined by `MBEDTLS_SSL_MAX_CONTENT_LEN`. You can safely reduce this to a more appropriate size (such as 2 KB) if:

* Both sides support the `max_fragment_length` SSL extension (allowing reduction to under 1 KB for the buffers).
* You know the maximum size that will ever be sent in a single SSL/TLS frame (whether or not you control both sides of the connection).

## AES

### Storing AES tables in ROM

By default, our AES implementation uses tables that are computed the first time AES is used and then stored in RAM. You can store them in ROM by enabling `MBEDTLS_AES_ROM_TABLES`. This is a RAM-ROM trade-off.

## X.509

### Parsing X.509 certificates without copying the raw certificate data

The X.509 CRT parsing APIs `mbedtls_x509_crt_parse()` and `mbedtls_x509_crt_parse_der()` create an internal copy of the raw certificate data passed to them. While this allows you to free or reuse the input buffer, it means the raw certificate data will be twice in memory at some point.

To avoid that, the following API can be used to set up an X.509 certificate structure without making a copy of the input buffer:

```
int mbedtls_x509_crt_parse_der_nocopy( mbedtls_x509_crt *chain,
                                       const unsigned char *buf,
                                       size_t buflen );
```

The only difference between `mbedtls_x509_crt_parse_der_nocopy()` and `mbedtls_x509_crt_parse_der()` is that the buffer passed to `mbedtls_x509_crt_parse_der_nocopy()` holding the raw DER-encoded certificate must stay unmodified for the lifetime of the established
X.509 certificate context. See the [documentation](https://github.com/ARMmbed/mbedtls/blob/development/include/mbedtls/x509_crt.h) for more information.

_Example:_ If your own certificate and/or the trusted CA certificates are hardcoded in ROM, you may use `mbedtls_x509_parse_der_nocopy()` to create X.509 certificate contexts from them without an additional copy in RAM.

### Removing a peer certificate after the handshake

By default, Mbed TLS saves a copy of the peer certificate for the lifetime of an SSL session and makes it available through the public API `mbedtls_ssl_get_peer_cert()`. If the application does not need to inspect the peer certificate, disabling the compile-time option `MBEDTLS_SSL_KEEP_PEER_CERTIFICATE` saves RAM as the SSL module will not keep a copy of the peer certificate after the handshake.
The API `mbedtls_ssl_get_peer_cert()` to obtain the peer certificate is still present, but always returns `NULL`.

If you need to inspect the peer certificate during or immediately after the handshake, you may still disable `MBEDTLS_SSL_KEEP_PEER_CERTIFICATE` and inspect the certificate through a verification callback instead. A verification callback is a function called during the verification of the peer certificate chain and can be registered via `mbedtls_ssl_conf_verify()`. For example, the test application `ssl_client2` uses a verification callback to provide a readable description of the peer certificate for debugging purposes. Also, you may use this callback to make a copy of the peer certificate, in case you want to manage it yourself.

## Example configurations

We provide a few example configurations in the `configs` directory. Two of them feature footprint optimization for a specific usage profile:

* [`config-suite-b.h`](https://github.com/ARMmbed/mbedtls/blob/development/configs/config-suite-b.h) is a minimal configuration supporting NSA Suite B.
* [`config-ccm-psk-tls1_2.h`](https://github.com/ARMmbed/mbedtls/blob/development/configs/config-ccm-psk-tls1_2.h) is a minimal configuration supporting pre-shared key and with AES-CCM.
