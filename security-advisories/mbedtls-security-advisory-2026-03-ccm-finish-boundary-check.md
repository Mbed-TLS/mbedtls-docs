# CCM multipart finish tag-length validation bypass (CVE pending)

**Title** | CCM multipart finish tag-length validation bypass
--------- | ----------------------------------------------------------
**CVE** | Pending
**Date** | 31 March 2026
**Affects** | All versions of Mbed TLS from 3.1.0 to 3.6.5
**Not affected** | Mbed TLS 3.6.6 and later 3.6 versions, Mbed TLS 4.0.0 and later 4.x versions
**Impact** | Out-of-bounds read leading to information disclosure from CCM context memory
**Severity** | HIGH
**Credits** | Eva Crystal (0xiviel)

## Vulnerability

In the CCM implementation (`library/ccm.c`), the function `mbedtls_ccm_finish()` copies the authentication tag from the internal 16-byte buffer `ctx->y` into a caller-provided buffer using the caller-supplied `tag_len` parameter.

In Mbed TLS 3.6.5 and earlier 3.x versions, `mbedtls_ccm_finish()` is part of the public multipart CCM API and can be called directly by applications. Prior to the fix, the function did not validate that `tag_len` was within the valid CCM tag size range (4–16 bytes, even values only), nor did it enforce an upper bound of 16 bytes corresponding to the size of `ctx->y`.

As a result, an application that calls the multipart CCM API with a `tag_len` greater than 16 can trigger the following copy:

```
memcpy(tag, ctx->y, tag_len);
```

This causes a read beyond the end of the 16-byte `ctx->y` buffer and into adjacent members of the `mbedtls_ccm_context` structure. Depending on memory layout, this may disclose internal CCM state, including nonce/counter data, length fields, mode parameters, and block cipher context state.

In Mbed TLS 4.x development versions prior to the fix, the same missing validation exists in the internal implementation. However, `mbedtls_ccm_finish()` is not exposed as a public API in 4.x and is therefore not directly callable by applications through supported interfaces.

The one-shot CCM APIs (`mbedtls_ccm_encrypt_and_tag`, `mbedtls_ccm_auth_decrypt`) and PSA/cipher wrapper APIs are not affected, as they propagate a validated tag length consistently through setup and finish.

## Impact

In Mbed TLS 3.6.5 and earlier 3.x versions, an application that supplies an oversized tag_len to mbedtls_ccm_finish() via the public multipart CCM API can trigger an out-of-bounds read of up to tag_len - 16 bytes beyond the 16-byte internal ctx->y buffer.

This may result in disclosure of adjacent fields within the CCM context structure, which can include key-dependent block cipher state. The vulnerability is limited to an out-of-bounds read; it does not permit modification of memory and does not directly enable code execution. Exploitation requires the ability to invoke the multipart CCM API with controlled parameters.

## Affected versions

Mbed TLS 3.1.0 through 3.6.5 that include the multipart CCM API without validation of `tag_len` in `mbedtls_ccm_finish()` are affected.

In Mbed TLS 4.x versions the same validation issue exists internally but the function is not exposed via the public API.

## Work-around

- Avoid exposing the raw multipart CCM API to untrusted callers; use the one-shot CCM APIs or PSA/cipher wrappers instead.
- If the multipart CCM API must be used, ensure callers pass the same `tag_len` to `mbedtls_ccm_finish()` that was negotiated in `mbedtls_ccm_set_lengths()`.

## Resolution

Upgrade to a version that validates `tag_len` in `mbedtls_ccm_finish()` against CCM tag size constraints and the 16-byte internal buffer size.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.x | Mbed TLS 4.x |
| ------ | -------------- | ----------------- | ------------ |
| Basic fix | 53ab8a5 | c519064 | n.a |
| With tests and documentation | branch up to d6f635e..73c6d6d | branch up to d6f1bad..b856f85 | n.a |
