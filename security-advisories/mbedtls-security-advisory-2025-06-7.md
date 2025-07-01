# Misleading memory management in `mbedtls_x509_string_to_names()`

**Title** | Misleading memory management in `mbedtls_x509_string_to_names()`
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-47917
**Date** | 30 June 2025
**Affects** | All versions of Mbed TLS up to 3.6.3
**Not affected** | Mbed TLS 3.6.4 and later 3.6 versions, upcoming 4.x versions.
**Impact** | Possible use-after-free or double-free leading to arbitrary code execution.
**Severity** | HIGH
**Credits** | Found by Linh Le and Ngan Nguyen from Calif.

## Vulnerability

The function `mbedtls_x509_string_to_names()` takes a `head` argument that is
documented as an output argument. The documentation does not suggest the
function will free that pointer, however the function does call
`mbedtls_asn1_free_named_data_list()` on that argument, which performs a deep
`free()`.

As a result, application code that uses this function relying only on documented
behaviour is likely to still hold pointers to the memory blocks that were
`free()`d, resulting in high risk of user-after-free or double-free.

In particular, the two sample programs x509/cert_write and x509/cert_req
were affected (use-after-free if the `san` string contains more than one DN).

## Impact

Depending on the application code, a use-after-free and/or double-free is
likely. Depending on the malloc() implementation, this is likely to lead to
arbitrary code execution.

## Affected versions

All versions of Mbed TLS up to 3.6.3 are affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.4 and/or apply the workaround
below (which is enforced in 3.6.4: passing something other than a pointer-to-NULL
will result in the function immediately returning an error).

## Work-around

Always passing a pointer-to-NULL as the `head` argument to
`mbedtls_x509_string_to_names()` avoids the problem. Moreover, this approach will continue to work in version 3.6.4 and later.

Applications that do not call `mbedtls_x509_string_to_names()` directly are not
affected. Internal uses of this function do not lead to memory management
errors.
