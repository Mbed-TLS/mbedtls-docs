# Fuzzing of Mbed TLS

This document describes public resources about fuzzing of Mbed TLS.

## Cryptofuzz

[Cryptofuzz](https://github.com/guidovranken/cryptofuzz) is a program by Guido Vranken that performs the same cryptographic operation in many crypto libraries and compares the results.

The Cryptofuzz project does not run instances of Cryptofuzz. [OSS-Fuzz](#oss-fuzz) does.

### Cryptofuzz integration

Each cryptographic library is integrated as a module: a file `modules/NAME/module.cpp` has code to dispatch operations to the library. Mbed TLS is integrated through two modules:

* [Mbed TLS](https://github.com/guidovranken/cryptofuzz/blob/master/docs/mbedtls.md) ([`mbedTLS`](https://github.com/guidovranken/cryptofuzz/tree/master/modules/mbedtls))
* [TF-PSA-Crypto](https://github.com/guidovranken/cryptofuzz/blob/master/docs/tf-psa-crypto.md) (`TF_PSA_Crypto`) (work in progress as of March 2024)

The Mbed TLS module was originally written and is primarily maintained by Guido Vranken. The TF-PSA-Crypto module is currently being written by Arm with much help from Guido.

### Building cryptofuzz

Cryptofuzz treats OpenSSL (or one of its forks) as the reference implementation that it compares the other libraries against. To work on Mbed TLS support in Cryptofuzz, you'll need:

* A reasonably recent Clang;
* A build of a reasonably recent OpenSSL, with some non-default options (so distro builds might not work);
* A recent Mbed TLS source.

Assuming you have the Cryptofuzz source in a directory `cryptofuzz`, the OpenSSL source in `cryptofuzz/openssl` and the Mbed TLS source in `cryptofuzz/mbedtls`, you can use the following build script.

````sh
#!/bin/sh

cat >/dev/null <<'EOF'
Prerequisites:
apt-get install clang libboost-dev
apt-get install libfuzzer-$(clang --version | grep -Eo '[0-9]+' | head -n 1)-dev

Ubuntu 22.04: clang fails to compile C++ programs out of the box.
Reported bug: https://bugs.launchpad.net/ubuntu/+source/llvm-toolchain-14/+bug/2038340
Workaround:
```
apt-get install libstdc++-12-dev
```

Ubuntu 22.04:
```
clang++ -fsanitize=address,undefined,fuzzer-no-link -D_GLIBCXX_DEBUG -O2 -g -DCRYPTOFUZZ_OPENSSL_110 -I/home/gilpes01/_/crypto/cryptofuzz/openssl/include -Wall -Wextra -std=c++17 -I include/ -I . -I fuzzing-headers/include -DFUZZING_HEADERS_NO_IMPL driver.o executor.o util.o entry.o tests.o operation.o datasource.o repository.o options.o components.o wycheproof.o crypto.o expmod.o mutator.o z3.o numbers.o mutatorpool.o ecc_diff_fuzzer_importer.o ecc_diff_fuzzer_exporter.o botan_importer.o openssl_importer.o builtin_tests_importer.o bignum_fuzzer_importer.o  -fsanitize=fuzzer third_party/cpu_features/build/libcpu_features.a  -o cryptofuzz
/usr/bin/ld: /usr/bin/ld: DWARF error: invalid or unhandled FORM value: 0x23
```
Seems to be a known bug with binutils 2.38, fixed in 2.39 (so Ubuntu 22.10+ should work):
https://github.com/llvm/llvm-project/issues/56994

EOF

set -e

export CC=clang CFLAGS="-fsanitize=address,undefined,fuzzer-no-link -O2 -g"
export CXX=clang++ CXXFLAGS="-fsanitize=address,undefined,fuzzer-no-link -O2 -g -I$PWD/openssl/include -DCRYPTOFUZZ_MBEDTLS -DCRYPTOFUZZ_TF_PSA_CRYPTO"

# Since e34981e902495bf8d18f50eedb5bc69587f67893, this is still necessary to
# build modules before calling the toplevel makefile.
[ -e repository_tbl.h ] || ./gen_repository.py

# Create a worktree with openssl and build it.
# Note that you need OpenSSL 3.x, not 1.1.1.
[ -d openssl ] || git clone https://github.com/openssl/openssl
# Enable "enable-md2" and "enable-rc5" because cryptofuzz needs them.
# Enable "no-makedepend" because otherwise openssl wants to regenerate its
# build dependencies each time you run `make`, which takes time, requires
# more perl modules, and uses absolute paths which make it impossible to
# mix working inside and outside Docker.
[ -e openssl/Makefile ] || ( cd openssl && ./config enable-md2 enable-rc5 no-makedepend )
make -C openssl
make -C modules/openssl OPENSSL_INCLUDE_PATH=$PWD/openssl/include OPENSSL_LIBCRYPTO_A_PATH=$PWD/openssl/libcrypto.a

# Create a worktree with mbedtls and build it.
[ -d mbedtls ] || git clone https://github.com/Mbed-TLS/mbedtls
grep -q '^#define MBEDTLS_PLATFORM_MEMORY' mbedtls/include/mbedtls/mbedtls_config.h || {
  mbedtls/scripts/config.py full
  mbedtls/scripts/config.py unset MBEDTLS_PSA_CRYPTO_BUILTIN_KEYS
}
make -C mbedtls/library libmbedcrypto.a
make -C modules/mbedtls MBEDTLS_INCLUDE_PATH=$PWD/mbedtls/include MBEDTLS_LIBMBEDCRYPTO_A_PATH=$PWD/mbedtls/library/libmbedcrypto.a
make -C modules/tf-psa-crypto MBEDTLS_INCLUDE_PATH=$PWD/mbedtls/include MBEDTLS_LIBMBEDCRYPTO_A_PATH=$PWD/mbedtls/library/libmbedcrypto.a

if [ -e cryptofuzz ] && {
     [ -e modules/mbedtls/module.a -a modules/mbedtls/module.a -nt cryptofuzz ] ||
     [ -e modules/tf-psa-crypto/module.a -a modules/tf-psa-crypto/module.a -nt cryptofuzz ]
   }
then
  rm cryptofuzz
fi
make LIBFUZZER_LINK="-fsanitize=fuzzer"
````

See also [Generic building documentation](https://github.com/guidovranken/cryptofuzz/blob/master/docs/building.md).

### Running Cryptofuzz

* To run cryptofuzz for some randomized testing, just run `./cryptofuzz`.
* To run a specific set of operations, pass the `--operations` option with a comma-separated list of operation names. The operation names match class names in [`cryptofuzz/operations.h`](https://github.com/guidovranken/cryptofuzz/blob/master/include/cryptofuzz/operations.h).
* To restrict the set of algorithms, you can pass `digests`, `--ciphers`, `--curves` (all with a comma-separated list of names). For the list of available names, see `repository_tbl.h` (generated during the build) or [`gen_repository.py`](https://github.com/guidovranken/cryptofuzz/blob/master/gen_repository.py) (search for `Add( Digest("...") )`, `Add( Cipher("...") )`, `Add( ECC_Curve("...", ...) )`).

Example:
```
./cryptofuzz --operations=SymmetricEncrypt,SymmetricDecrypt --ciphers=AES_128_ECB,AES_128_CBC
```

See also [Generic running documentation](https://github.com/guidovranken/cryptofuzz/blob/master/docs/running.md).

### Reproducing Cryptofuzz crashes

If Cryptofuzz finds a (potential) bug, it aborts and leaves a `crash-*` file. Common causes of bugs are a sanitizer-triggered abort, an assertion failure in a module or a discrepancy between a library's result and the OpenSSL result.

To run Cryptofuzz on a crash file:
```
./cryptofuzz --debug crash-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

## OSS-Fuzz

[OSS-Fuzz](https://github.com/google/oss-fuzz) is a software project that combines fuzzing-related tools with scripts to run those fuzzers on a large set of security-critical programs, including Mbed TLS. OSS-Fuzz also runs these programs on a regular basis.

### OSS-Fuzz reports

When the OSS-Fuzz infrastructure notices a fuzzer crash, the maintainers of the offending module are notified. For fuzzers where Mbed TLS is integrated, this includes the Mbed TLS security team.

Fuzzing crash reports become public after 90 days or when the crash is noticed as fixed.

### OSS-Fuzz integration

Mbed TLS is integrated in four Cryptofuzz projects:

* [bignum-fuzzer](https://github.com/google/oss-fuzz/tree/master/projects/bignum-fuzzer) (obsoleted by Cryptofuzz?)
* [cryptofuzz](https://github.com/google/oss-fuzz/tree/master/projects/cryptofuzz) — see [“Cryptofuzz”](#cryptofuzz)
* [ecc-diff-fuzzer](https://github.com/google/oss-fuzz/tree/master/projects/ecc-diff-fuzzer) (obsoleted by Cryptofuzz?)
* [mbedtls](https://github.com/google/oss-fuzz/tree/master/projects/mbedtls) — see [“Mbed TLS fuzz programs”](#mbed-tls-fuzz-programs)

### Mbed TLS fuzz programs

The [`program/fuzz`](https://github.com/Mbed-TLS/mbedtls/tree/development/programs/fuzz) directory contains several programs to fuzz key parsing in the PK module, X.509 certificate/CRL/CRT parsing, and TLS/DTLS handshakes and communication.

These programs, as well as a corpuse, were contributed by Philippe Antoine (catenacyber) and are now mostly maintained by Arm.

To reproduce a crash, just run `programs/fuzz/xxx_fuzz crash-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, preferably in a debug build to understand what's going on.
