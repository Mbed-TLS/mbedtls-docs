## Downloading and building

### Getting Mbed TLS

Mbed TLS releases are available in the [public GitHub repository](https://github.com/Mbed-TLS/mbedtls).
To download directly, use the following Git command:

```sh
git clone https://github.com/Mbed-TLS/mbedtls.git
```

### Building Mbed TLS

**Prerequisites to building the library with the provided makefiles:**
* GNU Make.
* A C toolchain (compiler, linker, archiver) that supports C99.
* Python 3.6 to generate the test code.
* Perl to run the tests.

If you have a C compiler such as GCC or Clang, just run `make` in the top-level
directory to build the library, a set of unit tests and some sample programs.

To select a different compiler, set the `CC` variable to the name or path of the
compiler and linker (default: `cc`) and set `AR` to a compatible archiver
(default: `ar`); for example:
```
make CC=arm-linux-gnueabi-gcc AR=arm-linux-gnueabi-ar
```
The provided makefiles pass options to the compiler that assume a GCC-like
command line syntax. To use a different compiler, you may need to pass different
values for `CFLAGS`, `WARNINGS_CFLAGS` and `LDFLAGS`.

To run the unit tests on the host machine, run `make test` from the top-level
directory. If you are cross-compiling, copy the test executable from the `tests`
directory to the target machine.

