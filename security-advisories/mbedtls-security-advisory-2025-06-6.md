# NULL pointer dereference after using `mbedtls_asn1_store_named_data()`

**Title** | NULL pointer dereference after using `mbedtls_asn1_store_named_data()`
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-48965
**Date** | 30 June 2025
**Affects** | all versions of Mbed TLS up to 3.6.3
**Not affected** | Mbed TLS 3.6.4 and later 3.6 versions, upcoming Mbed TLS 4.x versions
**Impact** | NULL pointer dereference (CWE-476)
**Severity** | MEDIUM
**Credits** | Found by Linh Le and Ngan Nguyen from Calif.

## Vulnerability

In some circumstances (see below), `mbedtls_asn1_store_named_data()` leaves its
output list with an item in an inconsistent state with `val.p == NULL` but
`val.len > 0`. In that case, future uses of the list, either by the same
function or by other functions, are likely to dereference `val.p`, a NULL
pointer.

There are two ways this can happen:

1. By calling `mbedtls_asn1_store_named_data()` directly.
2. By calling it indirectly via `mbedtls_x509_string_to_names()` or associated
   functions (listed below).

When calling `mbedtls_x509_string_to_names()` directly, the problem happens when
an item with a certain OID has already been entered into the list, then
`mbedtls_asn1_store_named_data()` is called with the same OID and `val_len = 0`.
It then `free()`s `val.p` as documented, but fails to update `val.len`. Calling
`mbedtls_asn1_store_named_data()` again with the same OID (and a length not
greater than the last non-zero length) will cause a NULL pointer dereference.
Using the list in other ways is likely to also cause a NULL dereference.

The fault in `mbedtls_asn1_store_named_data()` can also be triggered by
malicious input when used indirectly via the following string-parsing functions:

- `mbedtls_x509_string_to_names()`, 
- `mbedtls_x509write_crt_set_subject_name()`,
- `mbedtls_x509write_crt_set_issuer_name()`,
- `mbedtls_x509write_csr_set_subject_name()`.

With these functions, the incorrect behaviour is triggered by input strings that
contain at least two entries with the same type: one with a non-zero length, and
a subsequent one of length zero.

This causes the list to contain an item in an inconsistent state; the NULL
dereference itself will happen either in a subsequent call to
`mbedtls_x509_write_names()` using that list, or directly within the same call
to `mbedtls_x509_string_to_names()` (or one of its wrappers as listed above) if
there is another entry with the same type after the one of length zero.

Specifically, inputs like "DC=foo,DC=#0000" will parse apparently successfully,
but using the output list (or CRT/CSR structure) with other functions will cause
them to dereference a NULL pointer. Inputs like "DC=foo,DC=#0000,DC=bar" will
cause a NULL dereference directly in the string parsing function.

## Impact

NULL pointer dereference, leading to DoS on platforms with memory protection,
and possibly code execution on microcontrollers without an MMU or MPU.

## Affected versions

All versions of Mbed TLS up to Mbed TLS 3.6.3 included are affected.

The first fixed version is Mbed TLS 3.6.4.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.4 (or TF-PSA-Crypto 1.x / Mbed TLS
4.x once they are released).

## Work-around

Applications that do not call `mbedtls_asn1_store_named_data()` or any of the
string-parsing functions mentioned above are not affected. Applications that
call these functions only with trusted inputs are not affected.

Note that these functions are used to create certificates or CSRs; as a result,
applications that only use but do not create certificates or CSRs should not be
affected.
