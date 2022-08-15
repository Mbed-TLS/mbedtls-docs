# Mbed TLS automated testing and quality assurance

## Introduction

We are devoted to keeping the Mbed TLS code-base secure. We, therefore, put a lot of effort into our quality assurance and testing the code.

## Types of testing
Mbed TLS provids a variety of tests.

We automatically check:

* Compilation on different systems.
* Code coverage.
* Regressions, test vectors and corner cases.
* Interoperability with other SSL libraries.
* Different build configurations.
* Memory leaks.
* Memory integrity (bounds, initialization).

Mbed TLS uses a Buildbot environment to run these tests on a number of different environments.

## Test details

### Test Framework
Currently, there are over 6000 automated test vectors that run in the `tests/` directory when `make check` is run. In CMake, `make memcheck` runs these tests under Valgrind.

We have our own test framework for running these tests, which combines generic test functions with specific test values. The build system generates parsing-test applications, such as `test_suite_aes.ecb`, and runs them with the different test case inputs available. The system remains aware of the current configuration from `config.h` and ensures that only relevant tests are run.

A sample output for these tests looks like this:

```
$ ./test_suite_ecb
AES-128-ECB Encrypt NIST KAT #1 ................................... PASS
AES-128-ECB Encrypt NIST KAT #2 ................................... PASS
AES-128-ECB Encrypt NIST KAT #3 ................................... PASS
AES-128-ECB Encrypt NIST KAT #4 ................................... PASS
AES-128-ECB Encrypt NIST KAT #5 ................................... PASS
<snip>
AES-256-ECB Decrypt NIST KAT #10 .................................. PASS
AES-256-ECB Decrypt NIST KAT #11 .................................. PASS
AES-256-ECB Decrypt NIST KAT #12 .................................. PASS

----------------------------------------------------------------------------

PASSED (77 / 77 tests (0 skipped))
```

More information on the test suites and how to add more tests can be found in [this article](/kb/development/test_suites.md).

### Interoperability testing
Because our test vectors can only test individual functions, we also run interoperability tests to check live SSL connections against OpenSSL and GnuTLS.

The test script `tests/compat.sh` checks each available ciphersuite in the current build, as a server and a client, against Mbed TLS, OpenSSL and GnuTLS (when available). These tests are run for each protocol version, with and without client authentication. In total, over 1600 combinations are tested.

Depending on the settings, memory leaks are automatically checked for as well.

A sample output for these tests looks like this:

```
$ ./compat.sh
<snip>
P->P ssl3,no TLS-PSK-WITH-RC4-128-SHA .................................. PASS
P->P ssl3,no TLS-PSK-WITH-3DES-EDE-CBC-SHA ............................. PASS
P->P ssl3,no TLS-PSK-WITH-AES-128-CBC-SHA .............................. PASS
P->P ssl3,no TLS-PSK-WITH-AES-256-CBC-SHA .............................. PASS
P->P ssl3,no TLS-DHE-PSK-WITH-RC4-128-SHA .............................. PASS
P->P ssl3,no TLS-RSA-PSK-WITH-RC4-128-SHA .............................. PASS
P->O tls1,no TLS-ECDHE-ECDSA-WITH-RC4-128-SHA .......................... PASS
P->O tls1,no TLS-ECDHE-ECDSA-WITH-3DES-EDE-CBC-SHA ..................... PASS
P->O tls1,no TLS-ECDHE-ECDSA-WITH-AES-128-CBC-SHA ...................... PASS
P->O tls1,no TLS-ECDHE-ECDSA-WITH-AES-256-CBC-SHA ...................... PASS
P->O tls1,no TLS-ECDH-ECDSA-WITH-RC4-128-SHA ........................... PASS
P->O tls1,no TLS-ECDH-ECDSA-WITH-3DES-EDE-CBC-SHA ...................... PASS
<snip>
------------------------------------------------------------------------
PASSED (2143 / 2143 tests (0 skipped))
```

### Option testing
In addition to standard interoperability with other libraries, we also test for behaviors that should occur during a handshake or afterwards, by using the script `tests/ssl-opt.sh`.

A sample output for these tests looks like this:

```
$ ./ssl-opt.sh
<snip>
Session resume using cache #8 (openssl client) ......................... PASS
Session resume using cache #9 (openssl server) ......................... PASS
Max fragment length #1 ................................................. PASS
<snip>
Renegotiation #0 (none) ................................................ PASS
Renegotiation #1 (enabled, client-initiated) ........................... PASS
<snip>
Authentication #1 (server badcert, client required) .................... PASS
Authentication #2 (server badcert, client optional) .................... PASS
<snip>
Authentication #9 (client no cert, openssl server optional) ............ PASS
Authentication #10 (client no cert, ssl3) .............................. PASS
SNI #0 (no SNI callback) ............................................... PASS
SNI #1 (matching cert 1) ............................................... PASS
<snip>
DTLS reassembly: fragmentation, nbio (openssl server) .................. PASS
DTLS proxy: reference .................................................. PASS
DTLS proxy: duplicate every packet ..................................... PASS
DTLS proxy: duplicate every packet, server anti-replay off ............. PASS
DTLS proxy: inject invalid AD record, default badmac_limit ............. PASS
DTLS proxy: inject invalid AD record, badmac_limit 1 ................... PASS
DTLS proxy: inject invalid AD record, badmac_limit 2 ................... PASS
DTLS proxy: inject invalid AD record, badmac_limit 2, exchanges 2 ...... PASS
DTLS proxy: delay ChangeCipherSpec ..................................... PASS
DTLS proxy: 3d (drop, delay, duplicate), "short" PSK handshake ......... PASS
DTLS proxy: 3d, "short" RSA handshake .................................. PASS
<snip>
------------------------------------------------------------------------
PASSED (269 / 269 tests (0 skipped))
```

### Different build configurations
The script `tests/scripts/test-ref-configs.pl` builds and checks different build configurations.

The current configurations tested are:

 * A minimal TLS 1.1 configuration: `configs/config-mini-tls1_1.h`.
 * A Suite B compatible configuration: `configs/config-suite-b.h`.
 * A minimal modern PSK configuration, using TLS 1.2 and AES-CCM-8: `configs/config-ccm-psk-tls1_2.h`.
 * A configuration without the SSL modules, as used by Picocoin: `configs/config-picocoin.h`.

### Memory checks
We run both automatic and manual tests with the Valgrind memory checker, and with various sanitizers from GCC and Clang: ASan for memory bounds checking, MemSan to detect uninitialized memory issues, and UBSan to detect undefined behaviors, according to the C standard.

### Test systems

Currently, we test on the following operating systems:

 * Debian with Intel 32-bit, Intel 64-bit and ARM 32-bit.
 * FreeBSD i386.
 * Win32 32-bit and 64-bit.

With a mixture of the following compilers and IDE environments:

 * GCC, with CMake and Make.
 * Clang.
 * MinGW32.
 * MS Visual Studio 12.
 * armcc.

### Static analysis

The [Coverity static analysis scanner](http://scan.coverity.com) automatically checks the Mbed TLS source code for security issues before every new release. You can find more details on the [Mbed TLS page on Coverity](https://scan.coverity.com/projects/4583).

In addition, we manually use [Clang's static analyzer](http://clang-analyzer.llvm.org/), and more recently [Infer](http://fbinfer.com/), on our codebase.

### Fuzzing

We use [Codenomicon Defensics](http://www.codenomicon.com/products/defensics/) for fuzzing our (D)TLS server (all versions) and X.509 code before every new release.

<!--",what-tests-and-checks-are-run-for-mbedtls,"Short article on the different Quality enhancing tests Mbed TLS performs to increase trust in the library.",,"tests, memory checks, compat.sh",published,"2014-04-08 10:04:00",1,7917,"2016-02-26 22:42:00","Paul Bakker"-->
