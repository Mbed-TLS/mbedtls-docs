# Use-after-free in TLS 1.2 clients in renegotiation with variable buffer length (CVE-2026-93844)

**Title** | Use-after-free in TLS 1.2 clients in renegotiation with variable buffer length
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-93844
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions
**Impact** | Data leak and memory corruption in some calling applications
**CWE** | CWE-126: Buffer Over-read; CWE-416: Use After Free
**CAPEC** | CAPEC-123: Buffer Manipulation
**Severity** | HIGH
**Credits** | Alvaro Merino Argumanez (realvarx)

## Vulnerability

When TLS buffer resizing is enabled (`MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH`), the function `handle_buffer_resizing()` is called before and after a handshake. It may reallocate the input and output buffers to a different size, after which it updates pointers to the buffers in the SSL context.

This function forgot to update the field `in_offt`, which is a pointer to application data if there is data that has been received but not yet read by the application. The pointer is null if there is no pending data. During renegotiation, the pointer can be non-null, in which case it is left pointing to a freed buffer.

A renegotiation can happen at any time according to the TLS protocol. It has to be initiated by the client, however the library may do so automatically at the server's request, without an explicit request from the client application. Furthermore, regardless of which entity initiated the renegotiation, a malicious server can send application data while the renegotiation is ongoing, which is sufficient to trigger the bug.

## Impact

If a TLS 1.2 client starts a renegotiation while there is pending application data, a subsequent call to `mbedtls_ssl_read()` will output unrelated heap contents, which could potentially cause the application to leak sensitive information.

Furthermore, the area that the dangling pointer points to will eventually be zeroized, which may corrupt some heap objects or heap control structures.

## Affected versions

All versions of Mbed TLS up to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.1 are affected.
Mbed TLS from 4.2.0 is affected.

## Work-around

This vulnerability is only present if all of the following conditions are true:

* Renegotiation enabled at compile time (`MBEDTLS_SSL_RENEGOTIATION`, default enabled).
* Maximum fragment length support enabled at compile time (`MBEDTLS_SSL_MAX_FRAGMENT_LENGTH`, default enabled).
* Variable TLS buffer length enabled at compile time (`MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH`, default disabled).
* Renegotiation enabled at run time (`mbedtls_ssl_conf_renegotiation()`, default disabled).
* Maximum fragment length enabled at run time (`mbedtls_ssl_conf_max_frag_len()`, default disabled).

Thus disabling any of the above protects a client application from this vulnerability.

Additionally, a client can protect itself by never starting a renegotiation. If renegotiation is enabled, the library may initiate a renegotiation at the server's request, but it won't do so if the client has called `mbedtls_ssl_conf_renegotiation_enforced()` with `MBEDTLS_SSL_RENEGOTIATION_NOT_ENFORCED`.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
or to Mbed TLS 4.1.2 or a later 4.1.x version,
or to Mbed TLS 4.3.0 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- | -------------- | --------------------- |
| Basic fix | 11e7ea09227ed20cad311526f32d0a08b62a1065 dada1c172b3cbb298c8252d93b6ae090fa2223be 580aecfd76638dec48700c177108bbc0129b4df8 50bd87fcc9b7ac24fb43dc97a4ce64e315e37e71 | N/A | N/A | 4e300f4a17a0fdb7b0e602ac8cfa0ea1be92cac6 12f36c21ec19d3c995c7febb4f12ad8a9f72127c 2da4c3b05f7b9f78566402fba54456417ccfeff3 98da47bf90ec8e36d61e144e033017f6c810cf7e | 9f433e857595e301909836d0ba13c7ab0e550bf4 79a0573130070fe8a85f2f50d8db6777e3581380 f7e4ad9963d288a7792c7efe582480a2507cd189 78fc182730f8a09d2446fe2658a98c1c6ff686ba |
| With tests and documentation | 11e7ea09227ed20cad311526f32d0a08b62a1065^..50bd87fcc9b7ac24fb43dc97a4ce64e315e37e71 | N/A | N/A | 4e300f4a17a0fdb7b0e602ac8cfa0ea1be92cac6^..98da47bf90ec8e36d61e144e033017f6c810cf7e | 9f433e857595e301909836d0ba13c7ab0e550bf4^..78fc182730f8a09d2446fe2658a98c1c6ff686ba |
