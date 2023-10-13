# Mbed TLS coding standards

## Intro

This document describes Mbed TLS preferences for code formatting, naming conventions, API conventions, coding style, file structure, and default content in C code. For build and test scripts, see the [script coding standards](script-coding-standards.md).

<span class="notes">**Note:** There are situations where we deviate from this document for 'local' reasons.</span>

## Code Formatting

### Enforcement with uncrustify

In order to maintain a consistent coding style, the C code in Mbed TLS is formatted with [Uncrustify](https://github.com/uncrustify/uncrustify). The reference version of Uncrustify is 0.75.1; older or newer versions are not suitable because they give different results. See the [“Installing uncrustify”](uncrustify.md#installing-uncrustify) article for some tips.

#### Code style check script

A test on the continuous integration systems verifies that the C code has the expected style. The script [`scripts/code_style.py`](https://github.com/Mbed-TLS/mbedtls/blob/development/scripts/code_style.py) can check or fix the coding style.

To check that the coding style is correct (for example before submitting a pull request):
```sh
scripts/code_style.py
```

To enforce the coding style on specific files:
```sh
scripts/code_style.py --fix library/file_i_edited.c tests/suites/test_suite_i_also_edited.function
```

To enforce the coding style on all files checked into Git:
```sh
scripts/code_style.py --fix
```

#### Exceptions to enforcement

The automatic tool usually does a good job of making the code presentable, but it can sometimes make mistakes. It is possible to disable enforcement for a fragment of code by placing it between comments containing `*INDENT-OFF*` and `*INDENT-ON*` (despite the name, this controls all style enforcement, not just indentation). Do this only in egregious cases.

```c
    // normal code here
/* *INDENT-OFF* */
    // weird code here
/* *INDENT-ON* */
    // normal code here
```

Code in the `3rdparty` directory generally retains its original style, and is not subject to enforcement.

### K&R

Mbed TLS generally follows the style of *The C Programming Language*, Second Edition, 1988, by Brian Kernighan and Dennis Ritchie (“K&R2”). The main deviations are:

* Indentation is 4 spaces (like K&R2, not 5 spaces like K&R1). Do not use tabs.
* `case` is indented one level further than `switch`.
* The body of `if`, `for` or `while` must be on a separate line and surrounded with braces, even if it's a single statement.

### Indentation

Mbed TLS source code files use 4 spaces for indentation, **not tabs**, with a preferred maximum line length of 80 characters.

`case` is indented one level further than `switch`.

```c
switch (x) {
    case 0:
        zero();
        break;
    ...
}
```

Labels are indented at the same level as the enclosing block.
```c
int f()
{
    ...code...
    if (ret != 0) {
        goto exit;
    }
    ...code...
exit:
    ...cleanup...
    return ret;
}
```

Every code statement should be on its own line, except in `for` loop headers.

### Space placement

Put a space in the following places:

* Around binary operators: `(x + y) * z`
* After a comma: `f(x, y)`
* Before the asterisk in a pointer type: `int *p`
* Between `if`, `switch`, `while`, `for` and the opening parenthesis: `if (f(x))`
* Outside curly braces: `do { ... } while (!done)`, `struct mystruct s = { 0 }`
* Inside the curly braces around initializers: `int a[] = { 1, 2, 3 };`

Do not put a space in the following places:

* After the function or macro name in a function or macro call: `f(x, y)`
* Inside parentheses: `if (f(sizeof(int), (int) y))`
* Inside square brackets: `a[i + 1]`
* Before a comma: `f(x, y)`
* After a prefix unary operator: `if (!condition)`, `++x`
* Before a postfix unary operator: `x++`
* Between an array and the following opening bracket: `int a[2];`, `a[i]`
* Around field access symbols: `s.a`, `p->a`
* After the asterisk in a pointer type: `int *p`
* Between the asterisks double pointers types or derefences: `char **p`, `x + **p`

### Use of parentheses

`sizeof` expressions always use parentheses even when it is not necessary (when taking the size of an object):
```c
    memset(buf, 0, sizeof(buf));
```

### Usage and placement of braces

Braces (curly brackets) are **mandatory in control statements** such as `if`, `while`, `for`, even when the content is a simple statement.

Opening braces around compound statements are on the same line as the control statement if there is one. The closing brace has the same indentation as the line with the opening brace. It is generally alone on their line, except when followed by `else` or by the `while` of a `do ... while` statement.

```c
    do {
        x += f();
        if (x == 0) {
            continue;
        }
        x += g();
    } while (condition);
```

As an exception, **the opening brace of a function definition is on its own line**, in the leftmost column. This helps editors and other tools that treat non-indented braces as delimiting toplevel blocks.

```c
int f(void)
{
    return 42;
}
```

In compound type declarations, the opening brace is on the same line as the `struct`, `union` or `enum` keyword. The closing brace is on a separate line with the final semicolon.

```c
typedef struct {
    int x;
    int y;
} pair_t;
```

Compound initializers can be on a single line if they fit.

```c
pair_t z = { 1, 2 };
```

### Formatting of lists

When a function or macro call doesn't fit on a single line, put one argument per line or a sensible grouping per line. For example, in the snippet below, `input_buffer` and `input_size` are on a line of their own even though the call could fit on two lines instead of three if they were separated:
```c
    function_with_a_very_long_name(parameter1, parameter2,
                                   input_buffer, input_size,
                                   output_buffer, output_size);
```

Lists of items other than function arguments should generally have one item per line. Exceptions:

* It's ok to write simple structure initializers on a single line.
* In an array initialized with numerical data, pack a sensible and consistent number of items per line. The number of items per line should be a power of 2 to faciliate counting.

In lists of items such array initializers and enum definitions, do include the optional comma after the last element. This simplifies merging, reordering, etc.
```c
typedef enum {
    FOO_1,
    FOO_2,      // <- do put a comma here
} foo_t;
```
Exceptions: you can and omit the trailing comma in structure initializers that fit on one line, or if the last element must always remain last (e.g. a null terminator).

### Preprocessor directives

When using preprocessor directives to enable or disable parts of the code, use `#if defined` instead of `#ifdef`. Add a comment to the `#endif` directive if the distance to the opening directive is bigger than a few lines or contains other directives:
```c
#if defined(MBEDTLS_HAVE_FEATURE)
/* ten lines of code or other directives */
#endif /* MBEDTLS_HAVE_FEATURE */
```

## Naming conventions

### Name spacing

All public names (functions, variables, types, `enum` constants, macros) must start with either `MBEDTLS_` or `mbedtls_`, usually followed by the name of the module they belong to (and submodule if applicable), followed by a descriptive part. Macros and `enum` constants are uppercase with underscores; other names are lowercase with underscores:
```c
    mbedtls_x509_crt_parse_file()
    mbedtls_aes_setkey_decrypt()
```

Note that all externally linked functions must have a name starting with `mbedtls_` to avoid link-time conflicts, even if they are not declared in a public header. This also applies to global variables (which should be used very sparingly).

Exception: code implementing the PSA crypto API uses the `PSA_` and `psa_` prefixes. This includes official APIs as well as draft APIs that are on the PSA standards track. API extensions which are meant to remain specific to Mbed TLS, and internal functions, should use the `MBEDTLS_/mbedtls_` prefix, however there are many existing cases of using the `PSA_/psa_` prefix.

Exception: macros may have lowercase names if they behave exactly like normal variables and functions. In particular, function-like macros may have lowercase names only if they expand to an expression that evaluates each argument exactly once. Even in those cases, uppercase names are strongly preferred and new code should not use lowercase macro names for anything other than function replacement (like `#define mbedtls_printf printf`).

### Local names

Static functions can use the same naming scheme as non-static functions (`mbedtls_MODULE_frobnicate()` or `psa_frobnicate()`). This is convenient if they are made non-static later, for example for testing. They can also have shorter names if it's convenient. Keeping the module name (`MODULE_frobnicate()`) as a prefix makes it slightly easier to follow call stacks across modules, but it is not compulsory.

Macros defined only in the `library` directory should follow the same naming scheme as non-static functions (`MBEDTLS_MODULE_FOO` or `PSA_FOO`). They can use shorter names (omitting `MBEDTLS_`, the module name, or both) if it's convenient. However, avoid names without underscores as some embedded platforms define short macro names in their system headers. Exception: macros defined in headers used by alternative implementations or PSA drivers (including headers that they include) must start with `MBEDTLS_` or `PSA_`.

Function parameters and local variables need no name spacing. They should use descriptive names unless they're very short-lived or are used for simple looping or are "standard" names (such as `p` for a pointer to the current position in a buffer).

### Lengths and sizes

By default all lengths and sizes are in bytes (or in number of elements, for arrays). If a name refers to a length or size in bits (as is often the case for key sizes) then the name must explicitly include `bit`, for example `mbedtls_pk_get_bitlen()` returns the size of the key in bits, while `mbedtls_pk_get_len()` returns the size in bytes. In addition, the documentation should always mention explicitly if key sizes are in bits or in bytes.

`size` should refer to the capacity of a buffer, and `length` to the length of the contents. Most of the time these are interchangeable. A typical exception is when the output is written in a buffer, but the exact length is not known by the caller.

### Modules: `bignum_core`, `bignum_mod` and `bignum_mod_raw`

Generic conventions:

- `mbedtls_mpi_uint *` input operands should be named by capital letters starting at the beginning of the alphabet (`A`, `B`, `C`, ...).
- `mbedtls_mpi_uint` operands in turn should be named by lower case letters starting at the beginning of the alphabet (`a`, `b`, `c`)
- For the result `X` or `x` should be used depending on the type.
- `N` is generally used for the modulus.
- `T` is generally used for a temporary work area given to a function.
- An exception from this convention is where the naming of function parameters and local variables follows the literature (e.g. Handbook of Applied Cryptography)

Length parameters:

- For length of `mbedtls_mpi_uint *` buffers we use `limbs`.
- Length parameters are qualified if possible (e.g. `input_length` or `A_limbs`)

## API conventions

This section applies fully to classic `mbedtls_xxx()` APIs and mostly to the newer `psa_xxx()` APIs. PSA have their own [conventions described in the PSA Crypto API specification](https://arm-software.github.io/psa-api/crypto/1.1/overview/conventions.html) which take precedence in case of conflicts.

### Module contexts

If a module uses a context structure for passing around its state, the module should contain an `init()` and `free()` function, with the module or context name prepended to it. The `init()` function must always return `void`. If some initialization must be done that may fail (such as allocating memory), it should be done in a separate function, usually called `setup()`. The `free()` function must free any allocated memory within the context, but not the context itself. It must set to zero any data in the context or substructures:
```c
    mbedtls_cipher_context_t ctx;
    mbedtls_cipher_init(&ctx);
    ret = mbedtls_cipher_setup(&ctx, ...);
    /* Check ret, goto cleanup on error */
    /* Do things, goto cleanup on error */
    cleanup:
    mbedtls_cipher_free(&ctx);
```
The goal of separating the `init()` and `setup()` part is that if you have multiple contexts, you can call all the `init()` functions first and then all contexts are ready to be passed to the `free()` function in case an error happens in one of the `setup()` functions or elsewhere.

### Return type

Most functions should return `int`, more specifically `0` on success (the operation was successfully performed, the object checked was found acceptable, etc.) and a negative error code otherwise. Each module defines its own error codes, see `error.h` for the allocation scheme. Exceptions to this rule:

* Functions that can never fail should either return `void` (such as `mbedtls_cipher_init()`) or directly the information requested (such as `mbedtls_mpi_get_bit()`).
* Functions that look up some information should return either a pointer to this information or `NULL` if it wasn't found.
* PSA functions that can fail return a [`psa_status_t` value](https://arm-software.github.io/psa-api/crypto/1.1/overview/conventions.html#return-status).
* Some functions may multiplex the return value, such as `mbedtls_asn1_write_len()` returns the length written on success or a negative error code. This mimics the behavior of some standard functions such as `write()` and `read()`, except there is no equivalent to `errno`: the return code should be specific enough.
* Some internal functions may return `-1` on errors rather than a specific error code; it is then up to the calling function to pick a more appropriate error code if the error is to be propagated back to the user.
* Functions whose name clearly indicates a boolean (such as, the name contains "has", "is" or "can") should return `0` for false and `1` for true. The name must be clear: for example, `mbdtls_has_foobar_support()` will return `1` if support for foobar is present; by contrast, `mbedtls_check_foobar_support()` will return `0` if support for foobar is present (success) and `-1` or a more specific error code if not. All functions named `check` must follow this rule and return `0` to indicate acceptable/valid/present/etc. Preference should generally be given to `check` names in order to avoid a mixture of `== 0` and `!= 0` tests.
* Functions called `cmp` must return `0` if the two arguments are equal, and if it makes sense, should return `-1` or `1` to indicate which argument is greater.

### Limited use of in-out parameters

Function should avoid in-out parameters for length (multiplexing buffer size on entry with length used/written on exit) since they tend to impair readability. For example:
```c
mbedtls_write_thing(..., unsigned char *buf, size_t *len); // no
mbedtls_write_thing(..., unsigned char *buf, size_t buflen, size_t *outlen); // yes
```

For PSA functions, [input buffers](https://arm-software.github.io/psa-api/crypto/1.1/overview/conventions.html#input-buffer-sizes) have a `size_t xxx_size` parameter after the buffer pointer, and [output buffers](https://arm-software.github.io/psa-api/crypto/1.1/overview/conventions.html#output-buffer-sizes) have a `size_t xxx_size` parameter for the buffer size followed by a `size_t *xxx_length` parameter for the output length. This convention is also preferred in new `mbedtls_xxx` code, but older modules often use different conventions.

You can use in-out parameters for functions that receive a pointer to some buffer, and update it after parsing from or writing to that buffer:
```c
mbedtls_asn1_get_int(unsigned char **p,
                     const unsigned char *end,
                     int *value);
```
In that case, the `end` argument should always point to one past the one of the buffer on entry.

Also, contexts are usually in-out parameters, which is acceptable.

### `Const` correctness

Function declarations should keep `const` correctness in mind when declaring function arguments. Arguments that are pointers and are *not* changed by the functions should be marked as such:
```c
int do_calc_length(const unsigned char *str);
```

## Code structure

### ISO C99

The code uses the C99 ISO standard.

However, don't use variable-length arrays (VLAs) as they are not supported by all compilers/systems, and can cause problems for static analysis.

In addition, avoid using `const` values to size arrays or as part of rvalues for other constants, as this is not supported by (at least) MSVC.

### Proper argument and variable typing

Type function arguments and variables properly. Specifically, the `int` and `size` fields hold their maximum length in a platform-independent way. For buffer length, this almost always means using `size_t`.

For values that can't be negative, use unsigned variables. Keep the type in mind when building loops with unsigned variables.

When it's unavoidable that a `size_t` must be passed as an `int` function parameter, it's necessary to add a cast to avoid warnings on some compilers.

### `Goto`

Use of `goto` is allowed in functions that have to do cleaning up before returning from the function even when an error has occurred. It can also be used to exit nested loops. In other cases the use of `goto` should be avoided.

### Exit early and prevent nesting

Structure functions to exit or `goto` the exit code as early as possible. This prevents nesting of code blocks and improves code readability.

Most functions that need cleanup have a single cleanup block at the end. The label for this block can be `cleanup:` or `exit:` (or `error:` if the block is skipped on success); follow the established convention when extending an existing module. Code that uses bignum must use `cleanup:` for the sake of `MBEDTLS_MPI_CHK`.

### External function dependencies

Mbed TLS code should minimize use of external functions. Standard `libc` functions are allowed, but should be documented in the [KB article on external dependencies](what-external-dependencies-does-mbedtls-rely-on.md).

## Preprocessor

### Minimize code based on preprocessor directives

To minimize the code size and external dependencies, the availability of modules and module functionality is controlled by preprocessor directives located in `mbedtls/mbedtls_config.h`. Each module should have at least its own module define for enabling or disabling the module altogether. Other files using the module header should only include the header file if the module is actually available.

Since often systems that use Mbed TLS do not have a file system, functions specifically using the file system should be contained in `MBEDTLS_FS_IO` directives.

### Conditional compilation hygiene

The span of a conditional compilation directive should generally be a sequence of C instructions or declarations.

If necessary, the span can be an expression or a sequence of expressions. For example, this is acceptable:
```c
static char self_test_key = {
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
#if !defined(SUPPORT_128_BIT_KEYS)
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
    0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
#endif
};
```

This is acceptable, but deprecated:
```c
    if (
#if defined(MBEDTLS_USE_PSA_CRYPTO)
        psa_condition()
#else
        legacy_condition()
#endif
      )
        do_stuff();
```
Such code is generally more readable with an intermediate variable, thus the following style is preferred:
```c
#if defined(MBEDTLS_USE_PSA_CRYPTO)
    const int want_stuff = psa_condition();
#else
    const int want_stuff = legacy_condition();
#endif
    if (want_stuff)
        do_stuff();
```

Do not put partial instructions in a conditionally compiled span. For example, do not write the code above like this:
```c
#if defined(MBEDTLS_USE_PSA_CRYPTO)     // NO!
    if (psa_condition())                // NO!
#else                                   // NO!
    if (legacy_condition())             // NO!
#endif                                  // NO!
        do_stuff();                     // NO!
```
Having two instances of `if` in the source code, but only one actually compiled, is confusing both for humans and for tools such as indenters and linters.

Exception: the following idiom, with a chain of if-else-if statements, is accepted.
```c
#if defined(MBEDTLS_FOO)
    if (is_a_foo(type))
        process_foo(type, data);
    else
#endif /* MBEDTLS_FOO */
#if defined(MBEDTLS_BAR)
    if (is_a_bar(type))
        process_bar(type, data);
    else
#endif /* MBEDTLS_BAR */
    {
        return ERROR_NOT_SUPPORTED;
    }
```

Never have unbalanced braces in a conditionally compiled span. Exception: public headers can, and must, have `extern "C" {` and `}` guarded by `#ifdef __cplusplus`.

### Minimize use of macros

Only use macros if they improve readability or maintainability, preferably both. If macros seem necessary for maintainability but hinder readability, consider generating code from a Python script instead.

If possible, use the C core language rather than macros. For example, if an expression is used often, a `static inline` function is better because it provides type checks, allows the compiler to keep the function call when optimizing for size, and avoids problems with arguments evaluated more than once. However, if the expression needs to be a compile-time constant when its parameters are, this is a good reason to use a macro.

### Macro definition hygiene

When the code contains a macro call `MBEDTLS_FOO(x, y)`, it should behave as much as possible as if `MBEDTLS_FOO` was a function. Deviate from this only to the extent necessary to make the macro practical.

If the arguments of a macro are C expressions (they usually are), put parentheses around the argument in the expansion. For example:
```c
#define FOO_SIZE(bits) (((bits) + 7) / 8 + 4)
```
The expansion contains `((bits) + 7)`, not `bits + 7`, so that a call like `FOO_SIZE(x << 3)` is parsed correctly. As an exception, it's ok to omit parentheses if the argument is directly passed to a function argument (or comma operator): `#define A(x) f(x, 0)` is acceptable.

If the expansion of a macro is a C expression, put parentheses around the expansion. Continuing the example above, this is so that a call like `FOO_SIZE(x) * 2` is parsed correctly. As an exception, it's ok to omit parentheses if the expansion is a function call or other highest-precedence operator: `#define A(x) f(x, 0)` is acceptable.

If a macro expands to a statement, wrap it in `do { ... } while (0)` so that it can be used in contexts that expect a single statement. For example:
```c
#define MBEDTLS_MPI_CHK(f)       \
    do {                          \
        if ((ret = (f)) != 0)    \
            goto cleanup;        \
    } while (0)`
```
The expansion is not just `if ((ret = (f)) != 0) goto cleanup` because that would not work in a context like `if (condition) MBEDTLS_MPI_CHK(f()); else ++x;` (the `else` would get attached to the wrong `if`).

Follow the expression paradigm or the statement paradigm if possible. Other paradigms are permitted if necessary, for example a macro that expands to an initializer such as
```c
#define MBEDTLS_FOO_INIT {0, {0, 0}}
```
The expansion of a macro must not contain unbalanced parentheses, brackets or braces.

In macro expansions, do not make assumptions about the calling context, for example do not assume that a particular variable is defined. Exception: variable names with a very strong convention in the code base, like the `ret` example above which is systematically used for status codes in the classic mbedtls API. If the macro needs an intermediate variable, give it a long name that won't clash with anything else, but strongly consider using a function instead.

## Clear security-relevant memory after use

Memory that contains security-relevant information should be set to zero after use, and before being released to be reused. Use the function `mbedtls_platform_zeroize()` to prevent unwanted compiler optimization.

## Clear and free what you made

The module that allocated a piece of heap memory is also responsible for releasing it later on unless explicitly documented in the function definition in the header file.

## `Module self_test()`

Each module should have a self-test function (between a check for **MBEDTLS_SELF_TEST**). This function should test basic module sanity, but stay away from performing time-consuming tests.

## Doxygen documentation formatting

The header files should be documented with Doxygen-style code comments. Use the **'\'** character as a separator.

|Function|Description|
|---|---|
|\brief|A useless function present for documentation purposes.|
|\note|This function has no influence on code security.|
|\param buf|Buffer to ignore.|
|\param len|Length of buffer.|
|\return|0 if successfully ignored, otherwise, a module-specific error code.|

## Loose coupling interfaces

Each module should keep loose coupling with external modules and functions in mind. Use flexible function pointers over hard functions calls in cases where you want to replace part of the code with a local version.

## Generic file structure

### Header files

Structure header files as follows:

* Brief description of the file.
* Copyright notice and license indication.
* Header file define for `MBEDTLS_ {MODULE_NAME} _H`:
```c
#ifndef MBEDTLS_AES_H
#define MBEDTLS_AES_H
```
* Includes. Always include `<mbedtls/build_info.h>` before anything that might depend on the compile-time configuration.
* Public defines (Generic and error codes) and portability code.
* C++ wrapper for C code:
```c
#ifdef __cplusplus
extern "C" {
#endif
```
* For modules with optional alternative implementations, check for module specific structures:
```c
#if !defined(MBEDTLS_AES_ALT)
```
* Public structures that can have alternative implementations.
* For modules with optional alternative implementations, include the alternative header file:
```c
#else  /* MBEDTLS_AES_ALT */
#include "aes_alt.h"
#endif /* MBEDTLS_AES_ALT */
```
* Public structures that should not have alternative implementations.
* Function declarations.
* C++ end wrapper:
```c
#ifdef __cplusplus
}
#endif
```
* Header file end define:
```c
#endif /* MBEDTLS_AES_H */
```

### Source files

Source files are structured as follows:

* Brief description of the file.
* Copyright notice and license indication.
* Comments on possible standard documents used.
* Preprocessor directive for module:
```c
#if defined(MBEDTLS_AES_C)
```
* Includes. All library source files start by including `"common.h"`.
* If applicable, preprocessor directive for alternative implementation:
```c
#if !defined(MBEDTLS_AES_ALT)
```
* Private local defines and portability code.
* Function definitions.
* If applicable, preprocessor directive for marking the end of an alternative implementation:
```c
#endif /* !MBEDTLS_AES_ALT */
```
* Preprocessor directive for selftest (where applicable):
```c
#if defined(MBEDTLS_SELF_TEST)
```
* Self-test test vectors.
* Self test implementation.
* Preprocessor directive for marking the end of self tests (where applicable):
```c
#endif /* MBEDTLS_SELF_TEST */
```
* Preprocessor directive for marking the end of a module:
```c
#endif /* MBEDTLS_AES_C */
```

<!---mbedtls-coding-standards
,"Coding standards used in the Mbed TLS code, include default code formatting, coding style and file structures.","code formatting, coding style, file structures, code standards","code, formatting, style, coding style",published,"2012-10-18 11:34:00",3,7553,"2017-06-05 11:14:00","Paul Bakker"--->
