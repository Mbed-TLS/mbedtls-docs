# Mbed TLS CI failure FAQ

This guide is intended for contributors to Mbed TLS. It provides some tips to on investigating and resolving test failures in your contribution. It assumes basic familiarity with the CI jobs; please at least skim the [Mbed TLS CI guide](testing-ci.md).

## Understanding PR test failures

### PR tests failed. Which components failed?

If the PR tests fail, the status on GitHub is set to a string that lists failed components. Note that due to a GitHub limitation, the list of failed components may be truncated. Click the “Details” link to see the full job breakdown.

The default view on Jenkins unfortunately truncates job names. For more convenient access to the names and logs of failed components:

1. Install the GreaseMonkey/TamperMonkey user script [JenkinsPipelineSteps](https://openuserjs.org/scripts/magnushakansson/JenkinsPipelineSteps).
2. Go to the Jenkins “classic” view by clicking the ![Go to classic](jenkins-blueocean-go-to-classic.svg) icon near the top right, then follow the “Pipeline Steps” link in the left column.

Alternatively, you can extract the list of failed components from the list of failed test cases. See [“PR tests failed. Can I get a detailed list?”](#pr-tests-failed-can-i-get-a-detailed-list).

### PR tests failed. Can I get a detailed list?

You can download the list of failed test cases as an artifact on Jenkins. For example, the list of failures for the first test run of pull request \#9999 is at
```
https://mbedtls.trustedfirmware.org/job/mbed-tls-pr-head/job/PR-9999-head/1/artifact/failures.csv
```

If there are a large number of failures, the file will be compressed: add a `.xz` suffix to the URL.

The failure list consists of the lines of the [outcome file](testing-ci.md#outcome-analysis) where the status is FAIL.

### Analyzing `outcomes.csv` or `failures.csv`

Here are a few examples of Linux/macOS/Unix/WSL shell commands that can help.

#### In which components did this test case fail?

List the components where the test case “Test the thing” in `test_suite_foo` failed:
```
grep ';test_suite_foo;Test the thing;' failures.csv | cut -d ';' -f 2 | sort
```

Also list the components where it passed:
```
xzcat outcomes.csv.xz | grep ';test_suite_foo;Test the thing;' | grep -v ';SKIP;' | cut -d ';' -f 5,2 | sort
```

#### Which test cases failed at least once?

```
cut -d ';' -f 3,4 failures.csv | sort -u
```

### What is the configuration of this component?

Sometimes it can be hard to figure out exactly what configuration results from the code in `all.sh` and the rules to translate between PSA and legacy configuration options.

In a given build, you can run `programs/test/query_compile_time_config MBEDTLS_FOO; echo $?` to check whether `MBEDTLS_FOO` is enabled.

In the outcome file, the test suite reports the test case “Config: FOO” in `test_suite_config.*` as a PASS if the option FOO is enabled, and a SKIP if it is disabled. There are also test cases “Config: !FOO” which PASS if FOO is disabled and SKIP if it is enabled. Note that for some options, both FOO and !FOO are skipped if FOO has no effect because some other option is disabled.

### PR tests failed, but the failure list is empty!

Some failures are not recorded in the outcome file. In such cases, you need to look at the logs on Jenkins. Failures that are not recorded include:

* Static checks that don't involve a library build (code style, Python script checks, documentation build, etc.).
* Build failures in older branches (before [Mbed-TLS/mbedtls#9286](https://github.com/Mbed-TLS/mbedtls/pull/9286)).
* Checks that are run on a build that are not tests of the code, for example checking that a function is or is not present in a given configuration.
* At the time of writing, some minor test scripts do not record information in the outcome file, such as `*_demo.sh` and `tests/context_info.sh`.
* At the time of writing, Windows tests are not recorded in the outcome file.

### There are a lot of failures. Where do I start?

Most configurations are based on either the default configuration or the “full” configuration. The “full” configuration enables experimental and rarely-used features, and also toggles a few behavior change. Most importantly, in Mbed TLS 2.x and 3.x, `MBEDTLS_USE_PSA_CRYPTO` is disabled in the default configuration but enabled in “full”.

In terms of configurations, a suggested order is:

1. First, get the default configuration working.
2. Then the “full” configuration.
3. Then configurations that do not involve PSA drivers.
4. Finally, configurations involving PSA drivers.

### Outcome analysis failed

If you're unfamiliar with outcome analysis, please read the [outcome analysis section in the CI guide](testing-ci.md#outcome-analysis).

Outcome analysis may fail due to earlier failures, in which case you should resolve these failures and get updated CI results. In particular:

* Build failures or sanitizer crashes in some configuration may cause some test cases not to be executed.
* Failures in a driver build, or in the corresponding non-driver build (“reference”), may cause spurious differences to be reported.

The first step is generally to read the outcome analysis logs, which are available as an artifact, e.g.
```
https://mbedtls.trustedfirmware.org/job/mbed-tls-pr-head/job/PR-999-head/1/artifact/result-analysis-analyze_outcomes.log.xz
```

If a test case is reported as not executed: in which configurations would you expect it to run? Pick one and dive into the code to figure out why it isn't executed. If there is a good reason to have a test case that is not executed, add an exception. File an issue if the reason is temporary.

If there is a reported difference between a driver build and its reference build: run the test case in both configurations, and try to figure out why the behavior is different. If the difference can't reasonably be avoided, add an exception.

If outcome analysis complains that something was found in the ignore list but didn't need to be ignored, remove the exception from the ignore list.

## Reproducing failures locally

### How do I reproduce an `all.sh` failure locally?

First, [determine which component(s) failed](#pr-tests-failed-which-components-failed). See the [CI guide](testing-ci.md#high-level-overview-of-the-pr-tests) for an overview of component names.

Suppose that the CI status for PR tests is
```
Failures: all_u16-full_without_ecdhe_ecdsa all_u16-test_tls1_2_ccm_psk_dtls
```

You can run these `all.sh` components as follows:
```
tests/scripts/all.sh -k full_without_ecdhe_ecdsa test_tls1_2_ccm_psk_dtls
```

Note that this may or may not run successfully outside the [official Docker image](https://github.com/Mbed-TLS/mbedtls-test/tree/main/resources/docker_files). See the [CI tooling guide](testing-ci.md#tooling-for-allsh) for more information.

### Almost all tests fail in the full config

When `MBEDTLS_ENTROPY_NV_SEED` is enabled, any code that calls `mbedtls_entropy_init()` or `psa_crypto_init()`, which includes most tests other than low-level crypto tests, requires a seed file. For test purposes, the seed file can have any content, it just needs to be large enough (at least 64 bytes). The seed file is called `seedfile` and must be in the working directory where the test program runs, which is normally `tests`.

You can use one of the following commands to create a seed file:
```
head -c 64 </dev/urandom >tests/seedfile
truncate -s 64 tests/seedfile
```

If you run tests in different configurations successively in the same directory, you may end up with a smaller seed file. The seed file can be larger than required, but not smaller. If needed, just re-create a 64-byte seed file.

### How do I reproduce an `all.sh` failure in a debugger?

Most builds in `all.sh` have optimization enabled, and sometimes with sanitizers that might cause noise or incompatibilities with debuggers. If you want to look at the failure in a debugger, you'll need to look at the code of the component. The code of components is located in `tests/scripts/components-*.sh` (or within `tests/scripts/all.sh` itself in older branches).

Here are a few tips if you want to use `all.sh` directly:

* For builds that use CMake, run `cmake -D CMAKE_BUILD_TYPE=Debug` instead of the build type used in the test script. Alternatively, edit the lines that set `CMAKE_C_FLAGS_ASAN` in your local copy of `tests/scripts/all.sh` to give it the value `"-O0 -g3"` (don't commit the result).
* For builds that use plain make, pass `CFLAGS='-O0 -g3'`. If you're doing that a lot, edit the line that sets `ASAN_CFLAGS` in your local copy of `tests/scripts/all.sh` to be `ASAN_CFLAGS='-O0 -g3 -Werror'` (don't commit the result).
* `all.sh` will stop at the first failure, with the result of the partial build and any modified files, if you don't pass the `-k` (`--keep-going`) option.
* If you want to get the build products of a passing build by running `all.sh`, add `exit 1` in the component where you want to stop, then run `tests/scripts/all.sh component_name`.

### How do I reproduce driver builds with debug symbols?

The tips in [“How do I reproduce an `all.sh` failure in a debugger?”](#how-do-i-reproduce-an-allsh-failure-in-a-debugger) can help you get a debug build instead of an optimized+Asan build.

### How do I get multiple build trees with different configurations?

The provided `Makefile` does not support out-of-tree builds.

CMake supports out-of-tree builds. You can have a different configuration in different build trees as follows:

* Copy `mbedtls_config.h` under a different name, e.g.
    ```
    cp include/mbedtls/mbedtls_config.h include/foo-mbedtls_config.h
    ```
* Run `scripts/config.py -f include/foo-mbedtls_config.h` so that the file contains the desired configuration.
* If needed, do the same for `include/psa/crypto_config.h`.
* Create a build tree and run CMake with `CFLAGS` including `-DMBEDTLS_CONFIG_FILE="foo-mbedtls_config.h"` and if applicable `-DPSA_CRYPTO_CONFIG_FILE="foo-crypto_config.h"`. Pay attention to quoting in the shell! For example:
    ```
    mkdir build-foo
    cd build-foo-debug
    CFLAGS='-DMBEDTLS_CONFIG_FILE="foo-mbedtls_config.h" -DPSA_CRYPTO_CONFIG_FILE="foo-crypto_config.h"' cmake -DCMAKE_BUILD_TYPE=Debug
    make lib tests
    ```

Alternatively, the unofficial build tool [`mbedtls-prepare-build`](https://github.com/gilles-peskine-arm/mbedtls-docs/blob/mbedtls-prepare-build-3.4/tools/bin/mbedtls-prepare-build) is designed to support multiple build trees easily. For example:

```
mbedtls-prepare-build -p full-debug
mbedtls-prepare-build -d build-default-debug -p debug
mbedtls-prepare-build -d build-nosha1-debug -p debug --config-unset=MBEDTLS_SHA1_C
mbedtls-prepare-build -d build-norsa-debug -p full-debug --config-unset=MBEDTLS_PSA_CRYPTO_CONFIG,MBEDTLS_RSA_C,MBEDTLS_PKCS1_V15,MBEDTLS_PKCS1_V21,MBEDTLS_GENPRIME,MBEDTLS_X509_RSASSA_PSS_SUPPORT,MBEDTLS_KEY_EXCHANGE_DHE_RSA_ENABLED,MBEDTLS_KEY_EXCHANGE_RSA_PSK_ENABLED,MBEDTLS_KEY_EXCHANGE_ECDHE_RSA_ENABLED,MBEDTLS_KEY_EXCHANGE_ECDH_RSA_ENABLED,MBEDTLS_KEY_EXCHANGE_RSA_ENABLED
mbedtls-prepare-build -d build-suiteb-debug --config-file=configs/config-suite-b.h --config-set=MBEDTLS_DEBUG_C,MBEDTLS_ERROR_C
mbedtls-prepare-build -d build-accel-ecdsa-debug -p debug --config-set=MBEDTLS_PSA_CRYPTO_CONFIG --config-unset=MBEDTLS_PSA_CRYPTO_SE_C --accel-list=ALG_ECDSA,ALG_DETERMINISTIC_ECDSA,KEY_TYPE_ECC_PUBLIC_KEY,KEY_TYPE_ECC_KEY_PAIR_BASIC,KEY_TYPE_ECC_KEY_PAIR_IMPORT,KEY_TYPE_ECC_KEY_PAIR_EXPORT,KEY_TYPE_ECC_KEY_PAIR_GENERATE,KEY_TYPE_ECC_KEY_PAIR_DERIVE,ECC_SECP_R1_192,ECC_SECP_R1_224,ECC_SECP_R1_256,ECC_SECP_R1_384,ECC_SECP_R1_521,ECC_SECP_K1_192,ECC_SECP_K1_224,ECC_SECP_K1_256,ECC_BRAINPOOL_P_R1_256,ECC_BRAINPOOL_P_R1_384 -accel-list=ECC_BRAINPOOL_P_R1_512,ECC_MONTGOMERY_255,ECC_MONTGOMERY_448 --config-unset=MBEDTLS_ECDSA_C,MBEDTLS_KEY_EXCHANGE_ECDHE_ECDSA_ENABLED,MBEDTLS_KEY_EXCHANGE_ECDH_ECDSA_ENABLED --libtestdriver1-extra-list=ALG_SHA_224,ALG_SHA_256,ALG_SHA_384,ALG_SHA_512,ALG_SHA3_224,ALG_SHA3_256,ALG_SHA3_384,ALG_SHA3_512
```

## Other failed checks on GitHub

### Pre-test checks failed

If the pre-test checks failed, nothing was tested. Check the logs on Jenkins.

### Internal CI failed

Unfortunately, only Arm employees can have access to the Internal CI.

The Internal CI and OpenCI run the same tests, so please resolve failures on OpenCI first. If OpenCI passes but the corresponding Internal CI check fails, please ask an Arm employee for assistance.

### DCO check failed

Please see the [DCO section in the CI guide](testing-ci.md#dco).
