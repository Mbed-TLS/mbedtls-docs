# Mbed TLS CI

All code that is included in Mbed TLS must be contributed in the form of [pull requests on GitHub](https://github.com/Mbed-TLS/mbedtls/pulls) and undergoes some automated testing. This page describes the continuous integration jobs that run on every pull request.

## DCO

This job checks that all commits have a `Signed-off-by:` line. The presence of this line indicates that the author of the commit certifies that the commit is covered by the [Developer Certificate of Origin](https://github.com/Mbed-TLS/mbedtls/blob/development/dco.txt) and contributed according to the [project license](https://github.com/Mbed-TLS/mbedtls/blob/development/README.md#License).

All commits must have such a line, otherwise the commit cannot be accepted for legal reasons. As a temporary exception, commits from Arm employees or from other contributors who already have a contributor license agreement (CLA) can still be accepted, but please include a `Signed-off-by:` line in any new work.

If the DCO job fails, please reword all commit messages that are missing a `Signed-off-by:` line. If you have multiple commit messages to rewrite, [How to use git interactive rebase for signing off a series of commits](https://stackoverflow.com/questions/25570947/how-to-use-git-interactive-rebase-for-signing-off-a-series-of-commits) may help.

## PR-head and PR-merge jobs

The PR-//NNN//-head and PR-//NNN//-merge jobs run an extensive battery of tests on several platforms. The -head jobs run the tests on the tip of the submitted code. The -merge jobs run the tests on a merge with the target branch.

The PR-head job runs in public-facing CI every time a pull request is updated.

### High-level overview of the Jenkins test coverage

The Jenkins PR job includes the following parts:

- Run `tests/scripts/all.sh` on Ubuntu 16.04 x86 (64-bit). This script includes:
    - Some sanity checks.
    - Tests of the library in various configurations. The tests are mainly unit tests (`make test`), SSL feature tests (`tests/ssl-opt.sh`) and interoperability tests (`tests/compat.sh`).
    - Some cross compilation with GCC-arm, Arm Compiler 5 (`armcc`), Arm Compiler 6 (`armclang`) and MinGW (`i686-w64-mingw32-gcc`). These are only builds, not tests.
- Run a subset of `tests/scripts/all.sh` on FreeBSD (amd64)
- Build on Windows with MinGW and Visual Studio. We use the following Visual Studio versions:
    - Since Mbed TLS 2.19: VS 2013, 2015, 2017. As of January 2024, we expect to drop VS 2013 soon.

The component names are:

* all_sh-//platform//-//component//: `tests/scripts/all.sh -k `//component// run on //platform//.
* `code-coverage`: `tests/scripts/basic-build-test.sh` run on Linux (currently Ubuntu 16.04).
* `win32-mingw`, `win32_msvc12_32`, `win32-msvc12_64`: ad hoc Windows jobs in the default configuration, see below.
* `Windows-`//20NN//: builds with the specified version of Visual Studio (Visual Studio 10 2010, Visual Studio 12 2013, Visual Studio 14 2015 or Visual Studio 15 2017).
    * Library configuration: `config.py full` (`config.pl full` in older branches) minus `MBEDTLS_THREADING_xxx`.
    * Visual Studio configurations: `Release` and `Debug`.
    * Architectures: `Win32` and `x64` (except no `x64` in VS 2010).
    * `PlatformToolset` property:
        * “Retargeted” build: set to the version corresponding to the Visual Studio version for “retargeted” builds.
        * “Non-retargeted” build: set to `v120` on `development` (C99 code base).
    * Testing: `selftest.exe`, plus the unit tests in the CMake builds.

The `win32-mingw` component runs the following bat script:
```
cmake . -G "MinGW Makefiles" -DCMAKE_C_COMPILER="gcc"
mingw32-make
mingw32-make test
ctest -VV
programs\test\selftest.exe
```

The `win32_msvc12_32` component runs the following bat script:
```
call "C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\vcvarsall.bat"
cmake . -G "Visual Studio 12"
MSBuild ALL_BUILD.vcxproj
programs\test\Debug\selftest.exe
```
The `win32-msvc12_64` component is identical except that it runs `cmake . -G "Visual Studio 12 Win64"`.

## Tooling

### Tooling for all.sh

To run `tests/scripts/all.sh`, you need at least the following tools:

* basic Unix/POSIX shell utilities. Currently any modern `sh` should do, but a dependency on `bash` may be added in 2020.
* Git. `all.sh` requires a Git checkout. The following files may be restored to their checked-in version: `include/mbedtls/config.h`, `**/Makefile`.

`all.sh` is composed of many components, some of which have additional requirements. Most components require the following tools:

* `gcc` or `clang` (depending on the component) for native builds.
* GNU make or CMake (depending on the component).
* Perl 5.
* Python ≥3..
* The commands `openssl`, `gnutls-cli` and `gnutls-serv` must be present in the `$PATH` to run any test component (otherwise `all.sh` refuses to start). If you don't have them, you can still run some test components that don't do any interoperability testing with `env OPENSSL=false GNUTLS_CLI=false GNUTLS_SERV=false tests/scripts/all.sh …`.

### Running `all.sh` on Ubuntu

Our reference Linux platform is Ubuntu 16.04 x86 64-bit. More recent Ubuntu versions should also work.

On Ubuntu 16.04, the following packaged tools are known to cause problems with `all.sh`:

* The `gnutls-bin` package on Ubuntu 16.04 does not work with our test scripts because Ubuntu has removed some obsolete features.

On Ubuntu 20.04, the following packaged tools are known to cause problems with `all.sh`:

* `all.sh check_doxygen_warnings` fails. Doxygen 1.8.11 and 1.8.13 are known to work.

On Ubuntu, for the 32-bit builds, install the following packages:
```
apt-get install gcc-multilib libc6-dev-i386 linux-libc-dev:i386 libc6:386
```
Instead of `gcc-multilib`, which conflicts with cross-compilers for non-Intel architectures, a versioned package (e.g. `gcc5-multilib`) will do, but you need to create an additional symbolic link:
```
ln -s x86_64-linux-gnu/asm /usr/include/asm
```

### Notes about networking

The tests attempt to establish an IPv6 connection to the local host. This is optional, and will be skipped if IPv6 is not available. However, if IPv6 is possible but IPv6 connections to localhost are blocked by a firewall, the test will fail.
