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
    ```
    /* BEGIN_DEPENDENCIES
     * depends_on:MBEDTLS_CIPHER_C
     * END_DEPENDENCIES
     */
    ```

* `BEGIN_CASE` - When added to this delimiter, this specific test case will be generated at compile time only if the configuration option is defined in `mbedtls_config.h`.

    For example:
    ```
    /* BEGIN_CASE depends_on:MBEDTLS_AES_C */
    ```

## `helpers.function` file

This file, as its name indicates, contains useful common helper functions that can be used in the test functions. There are several functions, which are described in [`helpers.function`](https://github.com/ARMmbed/mbedtls/blob/development/tests/suites/helpers.function) itself. Following are a few common functions:

* `hexify()` - A function converting binary data into a null-terminated string. You can be use it to convert a binary output to a string buffer, to be compared with expected output given as a string parameter.
* `unhexify()` - A function converting a null-terminated string buffer into a binary buffer, returning the length of the data in the buffer. You can use it to convert the input string parameters to binary output for the function you are calling.
* `TEST_ASSERT(condition)` - A macro that prints failure output and finishes the test function (`goto exit`) if the `condition` is false.
* Different `rnd` functions that output different data, that you should use according to your test case. `rnd_std_rand()`, `rnd_zero_rand()`, `rnd_buffer_rand()`, `rnd_pseudo_rand()`. For more information on what each random function does, refer to their description in the `helpers.function` file.

## Building your test suites

The test suite `.c` files are auto generated with the `generate_code.pl` script. You could either use this script directly, or run `make` in the `tests/` folder, as the [`Makefile`](https://github.com/ARMmbed/mbedtls/blob/development/tests/Makefile) utilizes this script. Once the `.c` files are generated, you could build the test suite executables running `make` again. Running `make` from the Mbed TLS root folder will also generate the test suite source code, and build the test suite executables.

## Introducing new tests

When you want to introduce a new test, if the test function:

* Already exists and it only missing the test data, then update the .data file with the additional test data. If required, you can add a resource file to the `data_files/` subfolder.
* Doesn't exist, you can implement a new test function in the relevant `.function` file following the guidelines mentioned above and add test cases to the .data file to test your new feature.

If you need to define a new test suite, for example when you introduce a new cryptography module, update the [`Makefile`](https://github.com/ARMmbed/mbedtls/blob/development/tests/Makefile) to build your test suite.

You should write your test code in the same platform abstraction as the library, and should not assume the existence of platform-specific functions.

Note that SSL is tested differently, with sample programs under the `programs/ssl/` folder. These are executed when you run the scripts `tests/ssl-opt.sh` and `tests/compat.sh`.


## `.function` example

```
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
