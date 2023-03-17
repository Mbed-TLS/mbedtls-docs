# Building

Mbed TLS supports a number of different build environments out-of-the-box. However, the code and dependencies let you build with any environment.

## Prerequisites

* GNU Make, CMake or Visual Studio.
* A C toolchain (compiler, linker, archiver) that supports C99.
* Python 3.6 to generate the test code.
* Perl to run the tests.

## Building with Make

If using Make, you can build by running:
```
make
```
To run the test suite, run:
```
make check
```

To select a different compiler, set the `CC` variable to the name or path of the
compiler and linker (default: `cc`) and set `AR` to a compatible archiver
(default: `ar`); for example:
```
make CC=arm-linux-gnueabi-gcc AR=arm-linux-gnueabi-ar
```
The provided makefiles pass options to the compiler that assume a GCC-like
command line syntax. To use a different compiler, you may need to pass different
values for `CFLAGS`, `WARNINGS_CFLAGS` and `LDFLAGS`.


## Building with CMake

If you have CMake, the build process is better able to handle all the dependencies and do minimal builds. To build the source using CMake, run:
```
cmake .
make
```
In order to run the tests, enter:
```
make test
```
The test suites need Perl to be built. If you don't have Perl installed, you'll want to disable the test suites with:
```
cmake -DENABLE_TESTING=Off .
```
If you disabled the test suites, but kept the programs enabled, you can still run a much smaller set of tests with:
```
programs/test/selftest
```
To configure CMake for building a shared library, use:
```
cmake -DUSE_SHARED_MBEDTLS_LIBRARY=On .
```

### Switching build modes in CMake

CMake supports different build modes, to allow the stripping of debug information, or to add coverage information to the binaries.

The following modes are supported:

* **Release:** This generates the default code without any unnecessary information in the binary files.
* **Debug:** This generates debug information and disables optimization of the code.
* **Coverage:** This generates code coverage information in addition to debug information.
* **ASan:** This instruments the code with **AddressSanitizer** to check for memory errors. This includes **LeakSanitizer**, with recent versions of **gcc** and **clang**. With the most recent version of **clang**, this mode also uses **UndefinedSanitizer** to check for undefined behavior.
* **ASanDbg:** Same as **ASan** but slower, with debug information and better stack traces.
* **MemSan:** Uses **MemorySanitizer** to check for uninitialized memory reads. This is experimental, and needs the most recent **clang** on Linux/x86_64.
* **MemSanDbg:** Same as **MSan** but slower, with debug information, better stack traces and origin tracking.
* **Check:** This activates the compiler warnings that depend on optimization and treats all warnings as errors.

For debug mode, enter at the command line:
```
cmake -D CMAKE_BUILD_TYPE:Debug .
```
To list other available CMake options, use:
```
cmake -LH
```
Note that with CMake, if you want to change the compiler or its options after you already ran CMake, you need to clear its cache first:
```
find . -iname '*cmake*' -not -name CMakeLists.txt -exec rm -rf {} +
CC=gcc CFLAGS='-fstack-protector-strong' cmake .
```

## Windows Visual Studio 2013 and later

Inside Visual C++: open `visualc/VS2013/mbedTLS.sln` and select **Rebuild all**.

If you are using a later version of Visual Studio, it should prompt you to upgrade the files on first use. Accept this, and you are ready to build and compile.
