# Mbed TLS CI

All code that is included in Mbed TLS must be contributed in the form of [pull requests on GitHub](https://github.com/Mbed-TLS/mbedtls/pulls) and undergoes some automated testing. This page describes the continuous integration (CI) jobs that run on every pull request.

For tips on investigating CI failures, see the [Mbed TLS CI failure FAQ](understanding-ci-failures.md).

## Overview of the CI

The following checks are reported on GitHub:

* [DCO](#dco): check that all commit messages have a `Signed-off-by:` line. This must pass.
* [readthedocs](#documentation-build): build the documentation for online browsing. This must pass.
* [PR tests](#pr-tests): build and test the library in over 100 different configurations and platforms, as well as a few simple static checks. This must pass.
* [Interface stability tests](#interface-stability-tests): compare some interfaces before and after the proposed changes. This has many false positives, and a pull request can be merged if this check fails, at the gatekeeper's discretion.

The PR tests and the interface stability tests run on two hosts: “Internal CI” which is only accessible to Arm employees, and “TF OpenCI” which is publicly accessible. In principle, these run the same tests, thus if you are not an Arm employee (or even if you are) you can generally ignore the internal CI. At the time of writing, OpenCI is mandatory and internal CI is optional, so intermittent failures on the internal CI can be ignored.

## DCO

This job checks that all commits have a `Signed-off-by:` line. The presence of this line indicates that the author of the commit certifies that the commit is covered by the [Developer Certificate of Origin](https://github.com/Mbed-TLS/mbedtls/blob/development/dco.txt) and contributed according to the [project license](https://github.com/Mbed-TLS/mbedtls/blob/development/README.md#License).

All commits must have such a line, otherwise the commit cannot be accepted for legal reasons. For Arm employees or other contributors who already have a contributor license agreement (CLA), we can legally accept contributions without a DCO, however depending on the repository it may be technically impossible to merge a pull request with a failed DCO check.

If the DCO job fails, please reword all commit messages that are missing a `Signed-off-by:` line. If you have multiple commit messages to rewrite, [How to use git interactive rebase for signing off a series of commits](https://stackoverflow.com/questions/25570947/how-to-use-git-interactive-rebase-for-signing-off-a-series-of-commits) may help.

### Retrying a stuck DCO check

GitHub triggers a DCO check whenever a pull request is updated. This check is required: a pull request cannot be merged unless it passes.

If the DCO check doesn't report back to GitHub (the status remains “Pending” and no “Details” link appears), the only known solution is to change the commit ID at the head of the pull request. You can amend the head commit without changing its commit message: this changes the commit date, so it changes the commit ID. Force-pushing such an amended commit triggers all new CI checks, but does not invalidate review approvals.

## Documentation build

The Mbed TLS API documentation, rendered by Doxygen, is published [on readthedocs](https://mbed-tls.readthedocs.io/en/latest/). GitHub triggers a readthedocs build on every pull request. This is controlled by [`.readthedocs.yaml`](https://github.com/Mbed-TLS/mbedtls/blob/development/.readthedocs.yaml). This check is required: a pull request cannot be merged unless it passes.

### Retrying a stuck or failed documentation build

If the readthedocs build fails due to a transient failure (e.g. could not communicate to GitHub), or if the status is not reported back to GitHub due to a transient failure, you can re-trigger a new build in one of the following ways:

* If you have a readthedocs account with suitable permissions, go to the build page (`https://readthedocs.org/projects/mbedtls-versioned/builds/<NUMBER>/`) and click “Rebuild this build”.
* Close and reopen the pull request. This triggers a new readthedocs build, and preserves PR tests results and GitHub review states.

## PR tests

The “PR tests” (pull request tests) check is the bulk of the CI. It runs an extensive battery of tests on many configurations and with several toolchains and platforms. The tests are hosted on Jenkins.

This check must pass on at least one of the CIs (OpenCI or Internal CI). Which one is required can vary over time (depending on which one is most reliable and most convenient).

### High-level overview of the PR tests

The PR tests check includes the following parts:

- Run most of `tests/scripts/all.sh`. The default platform is on Ubuntu 16.04 x86 (64-bit), but some components request a different platform. This script includes:
    - Some sanity checks.
    - Tests of the library in various configurations. The tests are mainly unit tests (`make test`), SSL feature tests (`tests/ssl-opt.sh`) and interoperability tests (`tests/compat.sh`).
    - Some cross compilation with GCC-arm, Arm Compiler 5 (`armcc`), Arm Compiler 6 (`armclang`) and MinGW (`i686-w64-mingw32-gcc`). These are only builds, not tests.
- Run a subset of `tests/scripts/all.sh` on FreeBSD (amd64)
- Build on Windows with MinGW and Visual Studio. We use the following Visual Studio versions:
    - Since Mbed TLS 2.19: VS 2013, 2015, 2017. As of January 2024, we expect to drop VS 2013 soon.
- A final job called [outcome analysis](#outcome-analysis), which performs sanity checks on test coverage across builds in different configurations.

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

### Outcome analysis

Each build and test job saves a list of test cases and PASS/SKIP/FAIL information. The outcome analysis job collects this information and performs sanity checks on it. The collected data is called the outcome file, which is available as an artifact called `outcomes.csv.xz` on Jenkins. For example, you can download the outcome analysis for the first test run of pull request \#9999 at
```
https://ci.trustedfirmware.org/job/mbed-tls-pr-head/job/PR-9999-head/1/artifact/outcomes.csv.xz
```

Note that the outcome file is very large: on Mbed TLS 3.6, it is about 60MB compressed and over 2GB uncompressed.

The outcome file has a simple semicolon-separated format. The format is documented in [`docs/architecture/testing/test-framework.md`](https://github.com/Mbed-TLS/mbedtls/tree/development/docs/architecture/testing/test-framework.md#outcome-file).

If outcome analysis reports a failure, the logs can't be seen directly on the default view of Jenkins, due to a known limitation of Jenkins's BlueOcean interface. They can be accessed from the classic “Pipeline Steps” view. For convenience, they are also provided as an artifact, e.g.
```
https://ci.trustedfirmware.org/job/mbed-tls-pr-head/job/PR-999-head/1/artifact/result-analysis-analyze_outcomes.log.xz
```

Outcome analysis contains two kinds of checks:

* Every test case must be executed at least once.
* Driver builds must run the same sets of test cases as the corresponding builtin-only build (if there is one).

The script has a list of exceptions, which must be justified.

## Interface stability tests

The interface stability tests compare some aspects of the pull request's code with the code in the target branch. They run a script called `abi_check.py`, but their scope is broader than the name indicates:

* [API comparison](#api-comparison) in the default configuration;
* [ABI comparison](#abi-comparison) in the default configuration;
* Storage format [test case preservation](#test-case-preservation);
* Generated [test case preservation](#test-case-preservation).

These tests have many false positives. Therefore, it is not mandatory for them to pass. If GitHub marks the checks as failed, please see the logs and verify whether the reported failures are acceptable.

### API comparison

The API comparison checks that every API element in a public header that exists on the target branch still exists and is compatible on the pull request branch. This check is performed in the default configuration. For example, if a function exists on the main branch, there must be a function of the same name in the same header with the same prototype on the target branch.

The API must be preserved between minor versions of the library (e.g. Mbed TLS 3.4.x to Mbed TLS 3.5.0). It may only change in a major release (e.g. Mbed TLS 3.6.x to Mbed TLS 4.0.0).

Some changes are not considered API breaks, as described [in `BRANCHES.md`](https://github.com/Mbed-TLS/mbedtls/blob/development/BRANCHES.md#backwards-compatibility-for-application-code). There are acceptable changes which the tool flags, such as:

* Changes to private fields in structures (declared using `MBEDTLS_PRIVATE`).
* Changes to functions and macros that do not have Doxygen documentation.
* Changes to anything that is documented as experimental.

### ABI comparison

The ABI comparison checks that every symbol in a build in the default configuration of the target branch remains present in the target branch.

The ABI must normally be preserved between patch releases of the library (e.g. Mbed TLS 3.6.0 to Mbed TLS 3.6.1). In particular, it should be preserved in long-time support (LTS) branches. The ABI may change in minor or major releases (e.g. Mbed TLS 3.5.x to 3.6.0, or 3.6.x to 4.0.0).

There are acceptable changes which the tool flags, such as changes to undocumented functions that are only meant for use inside the library.

### Test case preservation

We check that certain sets of test cases are preserved.

* Storage format tests: the goal is to ensure that new versions of the library can read persistent keys stored by a previous version. We maintain this compatibility even across major versions. If the storage format changes, we will change the storage format version number and provide an upgrade path.
* Generated tests: the goal is to ensure that we don't lose coverage without noticing, for example if a change to a test generation script causes it to emit fewer tests than expected.

The comparison is based on lines in `.data` files containing the function name and the arguments for a test case. There are acceptable changes which the tool flags, such as adding an argument to a test function, or (not applicable to storage format tests) changes to the test data which we consider acceptable in terms of coverage.

## Tooling

This section describes some of the tooling needed to reproduce CI failures locally. Typical Linux or Mac developer machines have most of the necessary tooling, but not all. Note in particular that the SSL test scripts are written with specific versions of GnuTLS and OpenSSL in mind, and tend to have spurious failure when run against different versions.

For Linux-based tests, you can download Docker files with all the tools from the [mbedtls-test repository](https://github.com/Mbed-TLS/mbedtls-test/tree/main/resources/docker_files).

### Tooling for all.sh

To run `tests/scripts/all.sh`, you need at least the following tools:

* basic Unix/POSIX shell utilities. Currently any modern `sh` should do, but a dependency on `bash` may be added in 2020.
* Git. `all.sh` requires a Git checkout. The following files may be restored to their checked-in version: `include/mbedtls/config.h`, `**/Makefile`.

`all.sh` is composed of many components, some of which have additional requirements. Most components require the following tools:

* `gcc` or `clang` (depending on the component) for native builds.
* GNU make or CMake (depending on the component).
* Perl 5.
* Python ≥3.6 (different branches may have different version requirements).
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
