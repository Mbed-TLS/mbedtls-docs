# Building Mbed TLS as a contributor

## Introduction

### Purpose of this document

This guide is intended for maintainers and contributors of Mbed TLS and TF-PSA-Crypto. It discusses building the project when working on a contribution and investigating some common problems.

In particular, these projects have a wide range of possible configurations. Therefore a major aspect of this guide is how to work with multiple configurations.

### Developer platform

The primary platform for Mbed TLS and TF-PSA-Crypto is the latest or previous LTS release of Ubuntu Linux on x86_64. Other common platforms are likely to work too, including macOS and WSL, but some of the less common parts of the build system and test scripts may not be well-tested. The project accepts non-disruptive patches to improve the non-Linux experience.

Native Windows is not supported as a primary developer platform. The official build scripts do work on Windows, but you need Perl and Python even for basic usage, and a Unix-style shell for many maintainer scripts.

Some test scripts require specific versions of certain dependencies. See the [CI tooling guide](testing-ci.md#tooling-for-allsh) for more information.

You can get all the tooling necessary for all the test scripts (except Windows testing) from the Docker images that are used for the online continuous integration (CI). It is located in the [`mbedtls-test` repository](https://github.com/Mbed-TLS/mbedtls-test).

### Project-specific tooling

The [`mbedtls-docs` repository](https://github.com/Mbed-TLS/mbedtls-docs/tree/main/tools) has a few tools that can help maintainers and contributors.

### Available build systems

The following build systems are available for TF-PSA-Crypto and Mbed TLS:

* **CMake**. This is the only official build system in TF-PSA-Crypto 1.x and Mbed TLS 4.x.
* (Only up to Mbed TLS 3.6.x.) GNU make. The makefiles do not support out-of-tree builds and we will not discuss this build system further in this guide.
* (Only up to Mbed TLS 3.6.x; only on Windows.) Visual Studio solutions. Support for “exotic” configurations is limited. We will not discuss this build system further in this guide.
* (Unofficial) **[mbedtls-prepare-build](https://github.com/Mbed-TLS/mbedtls-docs/blob/main/tools/bin/mbedtls-prepare-build)**. This is an unofficial build system that supports most test configurations. It has some conveniences for project contributors that the official build scripts lack. it is shared alongside other unofficial tools in the [mbedtls-docs](https://github.com/Mbed-TLS/mbedtls-docs) repository. Beware that the version in the repository is very outdated, so you need at least the [latest pull request](https://github.com/Mbed-TLS/mbedtls-docs/pull/108).

## Setting up build directories

### Setup basics

#### Create a build directory and build

With CMake 3.13+, starting from the root of the source tree:

```
cmake -B build
make -C build
```

With CMake, using an existing directory (needed with CMake up to 3.12):

```
mkdir build
cd build
cmake ..
make
```

With mbedtls-prepare-build, starting from the root of the source tree:

```
mbedtls-prepare-build -d build
make -C build
```

#### Source and build directory location fine-tuning

| Task | CMake | mbedtls-prepare-build |
| ---- | ----- | --------------------- |
| Default build directory | current directory | current directory, but typically overridden by `-p/--preset` |
| Specify build directory | `-B` | `-d` |
| Default source directory | current directory | current directory |
| Specify source directory | `-S` | `-s` |

#### Setup presets

With CMake, you can select default compiler options (`CFLAGS`) through the **build type** with `cmake -D CMAKE_BUILD_TYPE=…`. To list available build types: ???

With mbedtls-prepare-build, you can select all settings (compiler options, compile-time config, cross-compilation, etc.) with a single **preset**: `mbedtls-prepare-build -p …`. This sets the default name for the build directory to `build-…`. To list available presets: `mbedtls-prepare-build --help`.

#### See what presets do exactly

With CMake: search `CMAKE_BUILD_TYPE` in `CMakeLists.txt`. Note that some build types are predefined and some effects depend on the compiler.

With mbedtls-prepare-build: search `_preset_options` in `mbedtls-prepare-build`.

#### Defining your own presets

With CMake, you can make a shell function that calls `cmake` and other tools as desired. On the `cmake` command line, if the same CMake variable is defined more than once, the last setting wins.

With mbedtls-prepare-build, you can make a shell alias that calls `mbedtls-prepare-build` with some options. With most options, if the same option is passed more than once, the last one wins. This is notably the case for `-p/--preset` and for options such as `--cflags` that are equivalent to an environment variable. However, a few options are additive and cannot be reset (`--config-set`, `--config-unset`, ...).

#### Command line completion

Bash (more precisely bash-completion) and zsh come with generic completion for CMake.

Zsh completion for mbedtls-prepare-build is available [in the mbedtls-docs repository](https://github.com/Mbed-TLS/mbedtls-docs/blob/main/tools/zsh/_mbedtls-prepare-build).

### Compiler options

#### Choose compiler and compiler flags manually

With CMake:

```
CC=clang CFLAGS='-O2 -std=c11' cmake -B build-clang-c11
```

With mbedtls-prepare-build:

```
CC=clang CFLAGS='-O2 -std=c11' mbedtls-prepare-build -d build-clang-c11
```

or

```
mbedtls-prepare-build -d build-clang-c11 --cc=clang --cflags='-O2 -std=c11'
```

or

```
mbedtls-prepare-build -d build-clang-c11 --cc clang --cflags '-O2 -std=c11'
```

#### Set up a debug build

With CMake:

```
cmake -DCMAKE_BUILD_TYPE=Debug -B build-debug
```

With mbedtls-prepare-build (the build directory defaults to `build-debug`):

```
mbedtls-prepare-build -p debug
```

#### Set up a build with ASan and UBSan

With CMake:

```
cmake -DCMAKE_BUILD_TYPE=Asan .. -B build-debug
```

With mbedtls-prepare-build (the build directory defaults to `build-debug`):

```
mbedtls-prepare-build -p asan
```

In both cases, the command line only mentions ASan (address sanitizer), but the build scripts also enable UBSan (undefined behavior sanitizer).

#### Set up a build with code size optimization

Both CMake and mbedtls-prepare-build default to `-Os` in `CFLAGS` if no build type is specified. See “[Choose compiler and compiler flags manually](#choose-compiler-and-compiler-flags-manually)” if you want a different choice.

With mbedtls-prepare-build, you can reproduce `component_build_arm_none_eabi_gcc_m0plus` from `all.sh` as follows:

```
mbedtls-prepare-build -p m0plus
```

You may be interested in [`mbedtls-size-dwim`](https://github.com/Mbed-TLS/mbedtls-docs/blob/main/tools/bin/mbedtls-size-dwim) (located alongside `mbedtls-prepare-build`) to track code size changes across successive commits.

#### Set up a build with code size optimization

With CMake, the build type `Release` sets the optimization level to `-O2` (`-Ohz` with IAR):

```
cmake -DCMAKE_BUILD_TYPE=Release -B build-opt
```

With mbedtls-prepare-build, the preset `opt` sets the optimization level to `-O3` (the build directory defaults to `build-opt`):

```
mbedtls-prepare-build -p opt
```

See “[Choose compiler and compiler flags manually](#choose-compiler-and-compiler-flags-manually)” if you want a different choice.

#### Set up a build for profiling

This section explains how to set up a build directory for profiling with GProf.
A profiling build requires specific compiler and linker options, so it is generally easier to set it up in a separate directory.

With CMake:

```
CFLAGS='-O2 -pg' LDFLAGS='-pg' cmake -B build-prof
```

With mbedtls-prepare-build, doing normal runs for `.run` targets by default:

```
mbedtls-prepare-build -d build-prof --cflags='-O2 -pg' --ldflags='-pg'
```

Then see “[Run tests with profiling](run-tests-with-profiling)”.

#### Set up a build for test coverage

This section explains how to set up a build directory for measuring test coverage with lcov.
Measuring test coverage requires specific compiler and linker options, so it is generally easier to set it up in a separate directory.

With CMake:

```
cmake -B build-coverage CMAKE_BUILD_TYPE=Coverage
```

With mbedtls-prepare-build:

```
mbedtls-prepare-build -p coverage
```

### Library configuration setup

#### Build in the full configuration

With CMake: ???

With mbedtls-prepare-build, you can use `--config-name=full` or one of the `full*` presets:

```
mbedtls-prepare-build -d build-full-custom --config-name=full
mbedtls-prepare-build -p full
mbedtls-prepare-build -p full-debug
mbedtls-prepare-build -p full-asan
```

#### Use a different configuration file (simple way)

You can select different configuration files (alternatives to `mbedtls/mbedtls_config.h` and `psa/crypto_config.h`) by setting the C preprocessor macros `MBEDTLS_CONFIG_FILE` and `TF_PSA_CRYPTO_CONFIG_FILE`. Both build systems can help with that.

With CMake, specify paths relative to the current directory:

```
cmake -B build-suiteb -D MBEDTLS_CONFIG_FILE=../configs/config-suite-b.h -D TF_PSA_CRYPTO_CONFIG_FILE=../configs/crypto-config-suite-b.h
```

With mbedtls-prepare-build, specify paths relative to the build directory:

```
mbedtls-prepare-build -d build-suiteb --crypto-config-file=../configs/crypto-config-suite-b.h --config-file=../configs/config-suite-b.h
```

#### Use a configuration file extension

You can select additional configuration files (effectively appended to `mbedtls/mbedtls_config.h` and `psa/crypto_config.h`) by setting the C preprocessor macros `MBEDTLS_USER_CONFIG_FILE` and `TF_PSA_CRYPTO_USER_CONFIG_FILE`.

With CMake, specify paths relative to the current directory:

```
cmake -B build-suiteb -D MBEDTLS_USER_CONFIG_FILE=tests/configs/user-config-for-test.h
```

User config files are not supported by mbedtls-prepare-build. You can use `--config-set` and `--config-unset` to tweak individual options, or [set the variables manually](#use-a-different-configuration-file-manual-way).

#### Use a different configuration file (manual way)

You can select different configuration files by setting the C preprocessor macros `MBEDTLS_CONFIG_FILE` and `TF_PSA_CRYPTO_CONFIG_FILE` via `CFLAGS`. In both cases, the value is what is after `#include`, so it requires double quotes or angle brackets around the file name; beware of quoting. Furthermore the file name must be either absolute, or relative to a directory that is in the include path.

With CMake (but note that modern versions of Mbed TLS have better support through CMake variables for the [main config files](#Use-a-different-configuration-file-simple-way) and [user config files](#use-a-configuration-file-extension)):

```
CFLAGS='-DMBEDTLS_CONFIG_FILE=\"../configs/config-tfm.h\" -Os' cmake -B build-tfm
```

With mbedtls-prepare-build:

```
mbedtls-prepare-build -d build-tfm --cflags '-DMBEDTLS_CONFIG_FILE=\"../configs/config-tfm.h\" -Os'
```

### Set individual options

You can set additional boolean options, or change the values of non-boolean options, by passing `-D` to the compiler in `CFLAGS`. See “[Choose compiler and compiler flags manually](#choose-compiler-and-compiler-flags-manually)”. This method does not allow unsetting options that are enabled by default.

With mbedtls-prepare-build, you can also use `--config-set`. [Completion](#command-line-completion) is available.

```
mbedtls-prepare-build -d build-custom --config-set=MBEDTLS_ECP_RESTARTABLE,MBEDTLS_ECP_WINDOW_SIZE=2
```

or

```
mbedtls-prepare-build -d build-custom --config-set=MBEDTLS_ECP_RESTARTABLE --config-set=MBEDTLS_ECP_WINDOW_SIZE=2
```

Limitation: at the time of writing, in Mbed TLS, mbedtls-prepare-build only tweaks options in `mbedtls_config.h`, so this doesn't work for crypto options with Mbed TLS 4.

### Set and unset individual options

CMake doesn't have a direct way to tweak individual config options. You can write `#define` and `#undef` directives in a header file and pass that as the [user config file](#use-a-configuration-file-extension). To run `config.py`, ???

With mbedtls-prepare-build, you can build a configuration incrementally:

* Start from `--config-file` (default: `include/mbedtls/mbedtls_config.h` in Mbed TLS, `include/psa/crypto_config.h` in TF-PSA-Crypto).
* Use `--config-name` to a named preset in `config.py`.
* Use `--config-set` and `--config-unset` to set and unset individual options. You can either pass the options more than once, or separate multiple options with a comma. [Completion](#command-line-completion) is available.

Limitation: at the time of writing, in Mbed TLS, mbedtls-prepare-build only tweaks options in `mbedtls_config.h`, so this doesn't work for crypto options with Mbed TLS 4.

```
mbedtls-prepare-build -d build-custom --config-set=MBEDTLS_ECP_RESTARTABLE,MBEDTLS_ECP_WINDOW_SIZE=2 \
    --config-unset=MBEDTLS_ECP_DP_{BP{256,381,512}R1,SECP{192,224,256}K1}_ENABLED
```

### Recreate a build directory

#### Reproduce a build directory

Suppose that `source1/build-foo` contains a build tree with settings that you like, and you want to set up a similar build tree in a different directory `source2`. This is common when making backports, or to share how to reproduce an issue.

With CMake: ???

With mbedtls-prepare-build, the first line of `Makefile` in the build directory contains the command line used to generate it.

```
$ head -n1 ../source1/build-foo/Makefile
Generated by /home/johndoe/bin/mbedtls-prepare-build -d build-foo --this --that
$ mbedtls-prepare-build -d build-foo --this --that
```

To set up another source directory on the same machine, you can leverage the undocumented variable `SOURCE_DIR`.

```
make -C ../source1/build-foo/Makefile SOURCE_DIR=$PWD dep
```

#### Refresh an existing build directory after changing dependencies

Suppose that you have a source tree with an existing build tree, and you modify some C source files in a way that affects the build: new source files, removed source files, or changed include directives.

CMake generally picks up updated dependencies automatically. (Are there limitations?) So just rebuild as usual.

With mbedtls-prepare-build, dependencies are analyzed only when you run the `mbedtls-prepare-build` command. If dependencies have changed, run `make dep` (or its alias `make prepare`) in the build directory.

```
mbedtls-prepare-build -d build-foo
make -C build-foo
# ... hackity hack ...
# E.g. add a new source file
make -C build-foo dep
make -C build-foo
```

If some files have been removed, you should run `make clean` in the build directory before re-running `make` or `make dep`. Otherwise obsolete build products may remain in the build tree, and they may confuse some scripts that enumerate build products with wildcards.

#### Refresh an existing build directory after changing generated files

CMake automatically rebuilds configuration-independent intermediate files as needed.

Limitation: mbedtls-prepare-build does not understand how the configuration-independent intermediate files are built. If they have changed, you need to regenerate them manually in the source tree first. (On first use, mbedtls-prepare-build generates all the configuration-independent intermediate files, but it doesn't detect when this needs to be re-done.)

In Mbed TLS, to update any intermediate file that needs updating:

```
make generated_files
```

In TF-PSA-Crypto, or in Mbed TLS, to unconditionally rebuild all intermediate files:

```
framework/scripts/make_generated_files.py
```

If build dependencies have changed in the generated files, [run `make dep` in the build tree](#refresh-an-existing-build-directory-after-changing-dependencies).

#### Refresh an existing build directory after changing branches

After changing branches, or rebasing an existing branch, the build scripts may have changed.

With CMake, ???

With mbedtls-prepare-build, run `make dep`  (or its alias `make prepare`) in the build directory in case the available files have changed. In some cases you should run `make clean` first, to avoid leaving obsolete build products behind. Furthermore, [you may need to refresh the generated files in the source tree](refresh-an-existing-build-directory-after-changing-generated-files).

In Mbed TLS, to update any intermediate file that needs updating:

```
make generated_files
make -C build-foo clean dep
```

In TF-PSA-Crypto, or in Mbed TLS, to unconditionally rebuild all intermediate files:

```
framework/scripts/make_generated_files.py
make -C build-foo clean dep
```

### Builds with drivers

#### Build with all drivers

CMake: ???

There is limited support for building with crypto drivers with mbedtls-prepare-build. It knows how to build the library, but needs assistance with the configuration. With Mbed TLS 3.6:

```
mbedtls-prepare-build -d build-drivers-debug -p debug --accel-list=all --cflags='-O0 -g3 -I../framework/tests/include -DPSA_CRYPTO_DRIVER_TEST_ALL -DMBEDTLS_USER_CONFIG_FILE=\"../tests/configs/user-config-for-test.h\"'
```

With TF-PSA-Crypto at the time of writing (May 2025):

```
mbedtls-prepare-build -d build-drivers-debug -p debug --accel-list=all --cflags='-O0 -g3 -I../framework/tests/include -DPSA_CRYPTO_DRIVER_TEST -DMBEDTLS_CONFIG_ADJUST_TEST_ACCELERATORS
```

(The option ` --accel-list=all` is needed to enable libtestdriver1 support in mbedtls-prepare-build. Its exact value does not matter but it must be alphanumeric and non-empty.)

#### Build with specific transparent drivers

CMake: ???

There is limited support for building with crypto drivers with mbedtls-prepare-build. You can use the following options:

* `--accel-list`: the PSA mechanisms to accelerate, with or without the `PSA_` prefix. You can pass the option multiple times and you can pass a comma-separated list each time. This is mandatory. It corresponds to `loc_accel_list` in `all.sh` components.
* `--libtestdriver1-extra-list`: additional mechanisms to enable in libtestdriver1, with or without the `PSA_` prefix. You can pass the option multiple times and you can pass a comma-separated list each time. This is optional. It corresponds to `loc_extra_list` in `all.sh` components.

For example, to redirect RSA via the test drivers, with no built-in fallback:

```
mbedtls-prepare-build -d build-accelrsa-debug -p debug --config-name=crypto_full \
    --accel-list=ALG_RSA_OAEP,ALG_RSA_PSS,ALG_RSA_PKCS1V15_CRYPT,ALG_RSA_PKCS1V15_SIGN,KEY_TYPE_RSA_KEY_PAIR_GENERATE,KEY_TYPE_RSA_KEY_PAIR_IMPORT,KEY_TYPE_RSA_KEY_PAIR_EXPORT,KEY_TYPE_RSA_PUBLIC_KEY \
        --libtestdriver1-extra-list=MBEDTLS_PEM_PARSE_C,MBEDTLS_BASE64_C,MBEDTLS_THREADING_C,MBEDTLS_THREADING_PTHREAD \
    --config-unset=MBEDTLS_RSA_C,MBEDTLS_PKCS1_V15,MBEDTLS_PKCS1_V21
```

Note: if multithreading support (`MBEDTLS_THREADING_C` and `MBEDTLS_THREADING_PTHREAD`) is enabled in the core configuration, it must also be enabled manually in the libtestdriver1 configuration, as shown in the example above.

### Cross-compilation

TODO

### Mimicking all.sh builds

TODO

## Build targets

### High-level build targets

#### Basic high-level build targets

Both build systems support a few basic high-level targets.

| Task | CMake | mbedtls-prepare-build |
| ---- | ----- | --------------------- |
| Build library, programs and tests | `make` or `make all` | `make` or `make all` |
| Build library | `make lib` in Mbed TLS, `make tfpsacrypto` in TF-PSA-Crypto | `make lib` |
| Build unit tests | ??? | `make tests` |
| Build and run unit tests | `make all test` | `make test` |
| Run already built unit tests | `make test` | `make test` (builds all tests first) |
| Build sample programs | ??? | `make programs` |
| Build for `ssl-opt.sh` and `compat.sh` | `make ssl-opt` | `make ssl-opt` |
| Remove build outputs | `make clean` | `make clean` |

#### Enumerate build targets

With CMake, `make help` lists all available targets. Note that some target files must be given by their full path, while others must be given by their base name only, and some files can only be built via other targets.

```
make -C build-foo help
```

With mbedtls-prepare-build, `make help` lists the main high-level targets with some brief documentation. In addition, all files that can be generated are available as targets.

```
make -C build-foo help
```

With either build systems, shell completion should find all targets with a modern fish, zsh or bash-completion.

### Build specific targets

#### Build a specific source file

With CMake, try `make help | grep source-file-base-name`. If you don't see the target you want, ???

With mbedtls-prepare-build, specify the path to the build output. This generally mimics the classic location in the mbedtls source tree: library sources (including Everest and p256-m) in `library`, programs in `programs/*`, test objects under `tests/src`, unit tests in `tests`.

```
make -C build-Os library/aes.o
make -C build-debug tests/test_suite_aes.ecb
```

#### Generate assembly

With CMake, try `make help | grep source-file-base-name.c.s`. (Note that the file has a double extension, with `.s` added to the source file name.) If you don't see the target you want, ???

With mbedtls-prepare-build, all target object files `*.o` have a corresponding target `*.s` for the compiler-generated assembly.

### Build control

#### Inspect shell command lines

With CMake, the default output is fancy and hides compiler command lines. Pass `SHELL='sh -x'` to see a trace of all shell commands.

```
make -C build-custom SHELL='sh -x'
```

With mbedtls-prepare-build, the default output is terse and hides compiler command lines. Pass `V=1` or `SHELL='sh -x'` to see all shell commands.

```
make -C build-custom V=1
```

#### Keep going on error

You can keep going on error with `make -k`. This is a make feature, independent of the makefile generator.

#### Parallel builds

You can build in parallel with e.g. `make -j2`. This is a make feature, independent of the makefile generator.

Note that running the tests in parallel is not well supported: this breaks with test suites that create PSA persistent keys. You can run tests sequentially with `make test`. With `ctest`, do not pass a `-j` option.

### Run unit tests

#### Run a specific test suite

With CMake, to build and run one test suite:

```
make -C build-debug test_suite_x509parse && build-debug/tests/test_suite_x509parse
```

(Note that the test programs are in the `tests` subdirectories, but the name of the build target is just the base name.)

With mbedtls-prepare-build, append `.run` to build and run the program.

```
make -C build-debug test_suite_x509parse.run
```

#### Run the all the tests for a multi-data function file

Some `test_suite_*.function` files have multiple associated data files `test_suite_*.*.data`. Each data file yields a corresponding executable. This section explains how to conveniently build all the executables from one `.function` file.

With CMake: ???

With mbedtls-prepare-build, in addition to `.run` target for each `.data` file, there is one associated with the `.function` file which runs all the executables.

```
make -C build-debug tests/test_suite_aes.run
```

#### Run a few unit tests, stopping on failure

This section explains how to build and run a specific list of unit tests, stopping on the first failure.

With CMake, you can build them all, then run them all. Is there a more convenient way???

```
make -C build-debug test_suite_x509parse test_suite_x509write && build-debug/tests/test_suite_x509parse && build-debug/tests/test_suite_x509write
```

With mbedtls-prepare-build, you can pass multiple `.run` targets. Note that `make` will automatically stop on the first failure.

```
make -C build-debug test_suite_x509parse.run test_suite_x509write.run
```

#### Run a few unit tests, continuing on failure

This section explains how to build and run a specific list of unit tests, continuing on failure and finishing with an indication of whether everything passed.

With CMake, you can build them all, then run them all. Is there a more convenient way???

```
make -C build-debug test_suite_x509parse test_suite_x509write && \
pass=true; for x in x509parse x509write; do build-debug/tests/test_suite_$x || pass=false; done; $pass
```

With mbedtls-prepare-build, you can pass multiple `.run` targets and use `make -k` to keep going on failure. (Note that this may re-run old executables if the build fails.)

```
make -C build-debug -k test_suite_x509parse.run test_suite_x509write.run
```

#### Run a test suite and hide passes

In large test suites, failures can be tedious to locate among passing and skipped tests. The following snippet hides `----` and `PASS` lines, but preserves all information about failure as well as test suite summaries.

```
tests/test_suite_ssl |& grep -Ev '(PASS|----)$'
```

#### Run all unit tests

With CMake, note that you need to build the unit tests before running `make test`. To build the unit tests ???

```
make -C build-debug all test
```

With mbedtls-prepare-build, to build and run all the unit tests:

```
make -C build-debug test
```

#### Exclude some test suites

To run most test suites, but exclude a few slower ones, you can use the `SKIP_TEST_SUITES` mechanism. The basic principle is the same in both build systems but the implementation is different.

With CMake, to select test suites to skip at the time you run the tests, ???

With CMake, pass a list of regular expressions to exclude in the test suite name as the `SKIP_TEST_SUITES` variable when you invoke CMake. The list elements can be separated by commas, spaces or semicolons. These test suites will be ignored in that build tree.

```
cmake -B build-fewer-tests SKIP_TEST_SUITES='constant_time_hmac,lmots,lms,gcm,psa_crypto.pbkdf2,ssl'
```

With mbedtls-prepare-build, pass a comma-separated list of regular expressions to exclude when you run the tests.

```
make -C build-debug SKIP_TEST_SUITES='constant_time_hmac,lmots,lms,gcm,psa_crypto.pbkdf2,ssl'
```

You can also set a default skip list for the build directory. It can then be overridden on the `make` command line.

```
mbedtls-prepare-build -p debug --var SKIP_TEST_SUITES='constant_time_hmac,lmots,lms,gcm,psa_crypto.pbkdf2,ssl'
```

#### Run unit tests under a wrapper

This section discusses how to run unit tests under a wrapper program such as `gdb`, `strace`, etc.

With CMake, build the unit tests, then run them manually. Is there another way???

```
make -C build-debug test_suite_ssl
build-debug/tests/test_suite_ssl -v
strace -o ssl.trace build-debug/tests/test_suite_ssl
gdb build-debug/tests/test_suite_ssl
```

With mbedtls-prepare-build, you can specify a shell command prefix through the `RUN` variable when you run `make`. If necessary you can also pass a suffix with `RUNS`.

```
make -C build-debug tests/test_suite_ssl.run RUNS=-v
make -C build-debug tests/test_suite_ssl.run RUN='strace -o ssl.trace'
make -C build-debug tests/test_suite_ssl.run RUN=gdb
```

#### Run unit tests with Valgrind

With CMake, to run a specific unit test with Valgrind: ???

With CMake, to run all the unit tests with Valgrind:

```
make -C build-debug memcheck
```

With mbedtls-prepare-build, to run a specific unit test with Valgrind, use the `.valgrind` target extension instead of `.run`.

```
make -C build-debug tests/test_suite_x509parse.valgrind
```

With CMake, to run all the unit tests with Valgrind:

```
make -C build-debug test.valgrind
```

#### Run tests with profiling

For profiling, you need to build with the right compiler and linker flags. See “[Set up a build for profiling](#set-up-a-build-for-profiling)”.

Note that the profiling data for GProf is written to a file called `gmon.out`. If you want to profile multiple executables in the same directory, you need to rename this file.

To perform a profiling run, with CMake:

```
make -C build-prof test_suite_ecp
build-prof/tests/test_suite_ecp
mv build-prof/tests/gmon.out build-prof/tests/test_suite_ecp.gmon
```

To perform a profiling run, with mbedtls-prepare-build:

```
make -C build-prof tests/test_suite_ecp.gmon
```

Then, to view the profiling report:

```
gprof build-prof/tests/test_suite_ecp.gmon
```

#### Measure test coverage

To measure test coverage, the tests must be built with coverage measurement enabled. See “[Set up a build for test coverage](#set-up-a-build-for-test-coverage)”.

To generate a coverage report, run `scripts/lcov.sh` from the root of the build tree.

```
make test # or whatever set of runs you want to measure cover for
cd build-coverage
../scripts/lcov.sh
```

With mbedtls-prepare-build, there is an `lcov` target that does the same job:

```
make test # or whatever set of runs you want to measure cover for
make -C build-coverage lcov
```

#### Creating the seedfile

In the `full` config, or more generally when `MBEDTLS_ENTROPY_NV_SEED` option is enabled, a file called `seedfile` must be present in the `tests` subdirectory of the build tree. This file must be at least 64 bytes long (the minimum is smaller in some configurations).

CMake automatically creates the seedfile when you run it.

With mbedtls-prepare-build, the seedfile is created the first time you run `make *.run` or `make test`.

In case something goes wrong and the file is not missing or too small (e.g. this can happen if `test_suite_entropy` crashes), you can create it manually with

```
echo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA >build-debug/tests/seedfile
```

The most obvious symptom of `seedfile` being missing or too small is that `psa_crypto_init()` fails with -148 (`PSA_ERROR_INSUFFICIENT_ENTROPY`).

