# Mbed TLS tests guidelines

Mbed TLS includes an elaborate amount of test suites in the `tests/` folder that initially requires Perl to generate the tests executable files. These files are generated from a function file and a data file, located in the `suites/` subfolder. The function file contains the test cases code, while the data file contains the test cases data, specified as parameters that will be passed to the test case code. In addition, some tests use data resource files (such as certificates and keys). They are in the `data_files/` subfolder. You should introduce new tests when you add a new feature to the library, or if you want to improve the test coverage.

Following are explanations on the `.function` and `.data` files that should assist you with adding your own test suite code.

Note that the test files are independent, and their order should not be dependent on each other.

## `.data` files

A test data file consists of a sequence of paragraphs separated by a single empty line. Each paragraph is referred as test case data. Line breaks may be in Unix (LF) or Windows (CRLF) format. Lines starting with the character '#' are ignored (the parser behaves as if they were not present). The first line must not be an empty line.

Each paragraph describes one test case and must consist of:

1. One line, which is the test case name.
1. An optional line starting with the 11-character prefix `depends_on:`. This line consists of a list of compile-time options separated by the character ':', with no whitespace. The test case is executed only if all of these configuration options are enabled in `mbedtls_config.h`. Note that this filtering is done at run time.
1. A line containing the test case function to execute and its parameters. This last line contains a test function name and a list of parameters separated by the character ':'. Each parameter can be any C expression of the correct type (only `int` or `char *` are allowed as parameters).

For example:

```
Parse RSA Key #8 (AES-256 Encrypted)
depends_on:MBEDTLS_MD5_C:MBEDTLS_AES_C:MBEDTLS_PEM_PARSE_C:MBEDTLS_CIPHER_MODE_CBC
pk_parse_keyfile_rsa:"data_files/keyfile.aes256":"testkey":0
```

## `.function` files

Code file that contains the actual test functions. The file contains a series of code sequences that the following delimit:

* `BEGIN_HEADER` / `END_HEADER` - Code that will be added to the header of the generated `.c` file. It could contain include directives, global variables, type definitions and static functions.
* `BEGIN_DEPENDENCIES` / `END_DEPENDENCIES` - A list of configuration options that this test suite depends on. The test suite will only be generated if all of these options are enabled in `mbedtls_config.h`.
* `BEGIN_SUITE_HELPERS` / `END_SUITE_HELPERS` - Similar to `XXXX_HEADER` sequence, except that this code will be added after the header sequence, in the generated `.c` file.
* `BEGIN_CASE` / `END_CASE` - The test case functions in the test suite. Between each of these pairs, you should write *exactly* one function that is used to create the dispatch code. Between the `BEGIN_CASE` directive and the function definition, you shouldn't add anything, not even a comment.

An optional addition `depends_on:` has same usage as in the `.data` files. The section with this annotation will only be generated if all of the specified options are enabled in `mbedtls_config.h`. It can be added to the following delimiters:

* `BEGIN_DEPENDENCIES` - When added in this delimiter section, the whole test suite will be generated only if all the configuration options are defined in `mbedtls_config.h`.

    For example:
    ```c
    /* BEGIN_DEPENDENCIES
     * depends_on:MBEDTLS_CIPHER_C
     * END_DEPENDENCIES
     */
    ```

* `BEGIN_CASE` - When added to this delimiter, this specific test case will be generated at compile time only if the configuration option is defined in `mbedtls_config.h`.

    For example:
    ```c
    /* BEGIN_CASE depends_on:MBEDTLS_AES_C */
    ```

## `helpers.function` file

This file, as its name indicates, contains useful common helper functions that can be used in the test functions. There are several functions, which are described in [`helpers.function`](https://github.com/Mbed-TLS/mbedtls/blob/development/tests/suites/helpers.function) itself. Following are a few common functions:

* `hexify()` - A function converting binary data into a null-terminated string. You can be use it to convert a binary output to a string buffer, to be compared with expected output given as a string parameter.
* `unhexify()` - A function converting a null-terminated string buffer into a binary buffer, returning the length of the data in the buffer. You can use it to convert the input string parameters to binary output for the function you are calling.
* `TEST_ASSERT(condition)` - A macro that prints failure output and finishes the test function (`goto exit`) if the `condition` is false.
* Different `rnd` functions that output different data, that you should use according to your test case. `rnd_std_rand()`, `rnd_zero_rand()`, `rnd_buffer_rand()`, `rnd_pseudo_rand()`. For more information on what each random function does, refer to their description in the `helpers.function` file.

## Building your test suites

The test suite `.c` files are auto generated with the `generate_code.pl` script. You could either use this script directly, or run `make` in the `tests/` folder, as the [`Makefile`](https://github.com/Mbed-TLS/mbedtls/blob/development/tests/Makefile) utilizes this script. Once the `.c` files are generated, you could build the test suite executables running `make` again. Running `make` from the Mbed TLS root folder will also generate the test suite source code, and build the test suite executables.

## Introducing new tests

When you want to introduce a new test, if the test function:

* Already exists and it only missing the test data, then update the .data file with the additional test data. If required, you can add a resource file to the `data_files/` subfolder.
* Doesn't exist, you can implement a new test function in the relevant `.function` file following the guidelines mentioned above and add test cases to the .data file to test your new feature.

If you need to define a new test suite, for example when you introduce a new cryptography module, update the [`Makefile`](https://github.com/Mbed-TLS/mbedtls/blob/development/tests/Makefile) to build your test suite.

You should write your test code in the same platform abstraction as the library, and should not assume the existence of platform-specific functions.

Note that SSL is tested differently, with sample programs under the `programs/ssl/` folder. These are executed when you run the scripts `tests/ssl-opt.sh` and `tests/compat.sh`.


## `.function` example

```c
/* BEGIN_HEADER */
#include "mbedtls/some_module.h"

#define MAX_SIZE     256
/* END_HEADER */

/* BEGIN_DEPENDENCIES
 * depends_on:MBEDTLS_MODULE_C
 * END_DEPENDENCIES
 */

/* BEGIN_CASE depends_on:MBEDTLS_DEPENDENT_MODULE */
void test_function_example( char *input, char *expected_output, int expected_ret )
{
    int ilen, olen;
    unsigned char buf[MAX_SIZE];
    unsigned char output[MAX_SIZE], output_str[MAX_SIZE];

    memset( buf, 0, sizeof( buf ) );

    ilen = unhexify( buf, input );

    TEST_ASSERT( mbedtls_module_tested_function( buf, len, output ) == expected_ret );

    if( ret == 0 )
    {
        hexify( output_str, output, olen );
        TEST_ASSERT( strcasecmp( (char *) output_str, output ) == 0 );
    }
}
/* END_CASE */
```

## Guidance on writing unit test code

### Testing expected results

Calls to library functions in test code should always check the function's return status. Fail the test if anything is unexpected.

The header file [`<test/macros.h>`](https://github.com/Mbed-TLS/mbedtls-framework/blob/development/tests/include/test/macros.h) declares several useful macros, including:

* `TEST_EQUAL(x, y)` when two integer values are expected to be equal, for example `TEST_EQUAL(mbedtls_library_function(), 0)` when expecting a success or `TEST_EQUAL(mbedtls_library_function(), MBEDTLS_ERR_xxx)` when expecting an error.
* `TEST_LE_U(x, y)` to test that the unsigned integers `x` and `y` satisfy `x <= y`, and `TEST_LE_S(x, y)` when `x` and `y` are signed integers.
* `TEST_MEMORY_COMPARE(buffer1, size1, buffer2, size2)` to compare the actual output from a function with the expected output.
* `PSA_ASSERT(psa_function_call())` when calling a function that returns a `psa_status_t` and is expected to return `PSA_SUCCESS`.
* `TEST_ASSERT(condition)` for a condition that doesn't fit any of the special cases.
    * In rare cases where a part of the test code shouldn't be reached, the convention is to use `TEST_ASSERT(!"explanation of why this shouldn't be reached")`.

### Buffer allocation

When a function expects an input or an output to have a certain size, you should pass it an allocated buffer with exactly the expected size. The continuous integration system runs tests in many configurations with Asan or Valgrind, and these will cause test failures if there is a buffer overflow or underflow.

For output buffers, it's usually desirable to also check that the function works if it's given a buffer that's larger than necessary, and that it returns the expected error if given a buffer that's too small.

Here is an example of a test function that checks that a library function has the desired output for a given input.
```c
/* BEGIN_CASE */
void test_function( data_t *input, data_t *expected_output )
{
// must be set to NULL both for TEST_CALLOC and so that mbedtls_free(actual_output) is safe
    unsigned char *actual_output = NULL;
    size_t output_size;
    size_t output_length;

    /* Good case: exact-size output buffer */
    output_size = expected_output->len;
    TEST_CALLOC( actual_output, output_size );
// set output_length to a bad value to ensure mbedtls_library_function updates it
    output_length = 0xdeadbeef;
    TEST_EQUAL( mbedtls_library_function( input->x, input->len,
                                          actual_output, output_size,
                                          &output_length ), 0 );
// Check both the output length and the buffer contents
    TEST_MEMORY_COMPARE( expected_output->x, expected_output->len,
                    actual_output, output_length );
// Free the output buffer to prepare it for the next subtest
    mbedtls_free( actual_output );
    actual_output = NULL;

    /* Good case: larger output buffer */
    output_size = expected_output->len + 1;
    TEST_CALLOC( actual_output, output_size );
    output_length = 0xdeadbeef;
    TEST_EQUAL( mbedtls_library_function( input->x, input->len,
                                          actual_output, output_size,
                                          &output_length ), 0 );
    TEST_MEMORY_COMPARE( expected_output->x, expected_output->len,
                    actual_output, output_length );
    mbedtls_free( actual_output );
    actual_output = NULL;

    /* Bad case: output buffer too small */
    output_size = expected_output->len - 1;
    TEST_CALLOC( actual_output, output_size );
    TEST_EQUAL( mbedtls_library_function( input->x, input->len,
                                          actual_output, output_size,
                                          &output_length ),
                MBEDTLS_ERR_XXX_BUFFER_TOO_SMALL );
    mbedtls_free( actual_output );
    actual_output = NULL;

exit:
    mbedtls_free( actual_output );
}
/* END_CASE */
```

### PSA initialization and deinitialization

In a test case that always uses PSA crypto, call `PSA_INIT()` at the beginning and `PSA_DONE()` at the end (in the cleanup section). Destroy all keys used by the test before calling `PSA_DONE()`: if any key is still live at that point, it is considered a resource leak in the test.

In a test case that uses PSA crypto only when building with `MBEDTLS_USE_PSA_CRYPTO`, call `USE_PSA_INIT()` at the beginning and `USE_PSA_DONE()` at the end.

See [`<test/psa_crypto_helpers.h>`](https://github.com/Mbed-TLS/mbedtls-framework/blob/development/tests/include/test/psa_crypto_helpers.h) for more complex cases.

## Guidance on writing unit test data

### Document the test data

Document how the test data was generated. This helps future maintainers if they need to generate more similar test data, for example to construct a non-regression test for a bug in a particular case.

The documentation can be:

* In Python (or other) code committed to the repository. This is preferred when the code can handle a large class of tests. For example, we have frameworks to generate key data for PSA, and to generate bignum tests. Some `.data` files are fully generated at build time by `tests/scripts/generate_*_tests.py`.
* In a comment in the `.data` file. This is more convenient when the instructions are specific to a single test case.
* In the commit that introduces the test data. This is more convenient when the instructions cover a series of similar test cases.

When adding a new file in `tests/data_files`, if possible, do it by editing `tests/data_files/Makefile` to add executable instructions for creating those files, and then run `make` and commit the result. Ideally removing the files and re-running `make` should produce identical files, however in many cases this is not practical because the generation is randomized or depends on the current time (for certificates and related data), and we accept that.

### Interoperability testing

Test data for cryptographic algorithms should be, in order of preference:

* Official test vectors taken from a standards document.
* Generated by a reference implementation from the authors of the algorithm, or by a widespread implementation such as OpenSSL or Cryptodome.
* Generated by another independent implementation.
* Obtained through manual means, possibly by patching together bits of other tests. For example, test output multipart operation function can be obtained by splitting the output of a one-shot operation function. Edge cases for parsing can be constructed by manually tweaking nominal cases.
* As a last resort, obtained by running the library once. This is a last resort since it cannot validate that the implementation is correct, it can only protect against future behavior changes. This should only be done when there is no other way, for example to construct a non-regression test in an edge case if we're very confident from code review that our bug fix is correct.

Whatever the source of the data is, remember to [document it](#document-the-test-data).
