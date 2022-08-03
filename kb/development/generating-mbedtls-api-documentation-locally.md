# Generating the API documentation locally

## Generating doxygen

Mbed TLS has full doxygen documentation in the source code which is also available on the site in the [API documentation page](https://tls.mbed.org/api).

To generate the documentation locally, [download](https://tls.mbed.org/download) and extract the latest Mbed TLS tarball and run:

    make apidoc
    
This generates the doxygen documentation in the `apidoc` subdirectory.
