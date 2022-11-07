# Deprecations

To ensure backwards-compatibility between versions of Mbed TLS, functions in the public interface may not be removed except during the release of a new major version. Instead, functions may be 'deprecated', indicating to users that they will be removed in the future.

To deprecate a function, the following actions must be taken:
* In the header file (e.g. `include/mbedtls/xyz.h`):
    * Make sure the header file includes `mbedtls/platform_util.h` (this contains the definition of `MBEDTLS_DEPRECATED`).
    * Surround the function declaration with `#if !defined(MBEDTLS_DEPRECATED_REMOVED)`.
    * Add a line to the docstring consisting of the keyword `\deprecated` followed by the reason for deprecation and (where applicable) the function it is superseded by.
    * Add the `MBEDTLS_DEPRECATED` annotation to the function prototype (so `int foo();` becomes `int MBEDTLS_DEPRECATED foo();`).
* In the source file (e.g. `library/xyz.c`):
    * Surround the function definition with `#if !defined(MBEDTLS_DEPRECATED_REMOVED)`.
    * If the function is superseded, ensure there is no code duplication between the old function and the new one. Typically this means refactoring the old function to be a simple wrapper around the new function.
* In a new file in ChangeLog.d (e.g. `ChangeLog.d/change-xyz-api.txt`)
    * Add an entry under the heading `New deprecations` that describes the deprecation. See [the ChangeLog readme](ChangeLog.d/00README.md) for more information on the format of ChangeLog entries.
* In the function's unit tests (see [the test guidelines](test_suites.md) for more information on unit tests):
    * Add `MBEDTLS_TEST_DEPRECATED` to the `depends_on:` line, either in the `.function` file or the `.data` file.

When a build is made with `MBEDTLS_DEPRECATED_WARNING` defined, a compiler warning will be generated to warn a user that the function will be removed at some point in the future, notifying users that they should change from the older deprecated function to the newer function at their own convenience. To find examples of deprecated functions, look at the previous LTS version of Mbed TLS.

## Deprecating constants

Numeric and string constants can also be deprecated by wrapping them in the macros `MBEDTLS_DEPRECATED_NUMERIC_CONSTANT()` and `MBEDTLS_DEPRECATED_STRING_CONSTANT()` respectively. For example, the code:
```c
const int X = 42;
```
would become:
```c
const int X = MBEDTLS_DEPRECATED_NUMERIC_CONSTANT(42);
```
