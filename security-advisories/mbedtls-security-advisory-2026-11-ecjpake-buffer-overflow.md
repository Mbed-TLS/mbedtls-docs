# ECJPAKE serialization can write beyond undersized output buffers (CVE-2026-90469)

**Title** | ECJPAKE serialization can write beyond undersized output buffers
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-90469
**Date** | 16 November 2026
**Affects** | Mbed TLS 3.3.0 through 3.6.7; Mbed TLS 4.0.0 through 4.1.1; Mbed TLS 4.2.x
**Not affected** | Mbed TLS 3.2.1 and earlier; Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later 4.x versions
**Impact** | A remote peer can cause memory corruption and potentially a denial of service in affected configurations
**CWE** | CWE-787: Out-of-bounds Write
**CAPEC** | CAPEC-100: Overflow Buffers
**Severity** | HIGH

## Vulnerability

When Mbed TLS serializes an ECJPAKE round, `mbedtls_psa_ecjpake_write_round()` reserves one byte before each output value to encode its length. The function did not first verify that this length byte fitted in the caller-provided buffer. If the preceding output exactly filled the remaining buffer, the output pointer advanced beyond the buffer and the capacity calculation underflowed, allowing `psa_pake_output()` to write beyond the buffer.

The vulnerable function is used when writing the ECJPAKE extension in TLS 1.2 ClientHello and ServerHello messages. Applications are affected when ECJPAKE and PSA-based cryptography are enabled and the extensions written before ECJPAKE leave too little space for a complete ECJPAKE round. This can occur even with the default `MBEDTLS_SSL_OUT_CONTENT_LEN` when locally configured extensions nearly fill the output buffer. Whether a particular buffer size is vulnerable depends on the enabled extensions, application configuration and runtime handshake parameters.

## Impact

A remote peer can cause an out-of-bounds write in an affected TLS or DTLS endpoint. This can corrupt memory and potentially terminate the process. The issue is rated HIGH.

## Affected versions

Mbed TLS 3.3.0 through 3.6.7 are affected.
Mbed TLS 4.0.0 through 4.1.1 are affected.
Mbed TLS 4.2.x versions are affected.

Mbed TLS 3.x applications are not affected when `MBEDTLS_USE_PSA_CRYPTO` is disabled.

## Work-around

Applications can avoid the vulnerability by disabling ECJPAKE or PSA-based ECJPAKE support.

For applications operating only as TLS or DTLS servers, setting `MBEDTLS_SSL_OUT_CONTENT_LEN` to at least 686 bytes prevents this overflow for all supported CID lengths. If `MBEDTLS_SSL_CID_IN_LEN_MAX` is at most 32 bytes (its default value), a value of at least 463 bytes is sufficient.

These bounds prevent this specific overflow; they do not guarantee that every handshake message fits in the output buffer.

For applications operating as clients, increasing `MBEDTLS_SSL_OUT_CONTENT_LEN` alone is not a configuration-independent workaround. Variable-length ClientHello extensions can in principle leave insufficient space for ECJPAKE even with the default output-buffer size, although this would be unlikely in practice and would typically require an unusually large application-configured value, such as a very large list of ALPN protocols.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
to Mbed TLS 4.1.2 or a later 4.1.x version,
or to Mbed TLS 4.3.0 or a later version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | --------------------- |
| Basic fix | `54866e2f148dd896d5449c792580b40d113a7f1d` | `e8fffa214525393ce37c236fcc3f7093014764bc` | `4efa93e7d4189ba1aa7ce1cfc41fde49edb40fb7` |
| With tests and documentation | `7963056a0fbe8fa7df1566dc32d9cc9ae57d1663^..f67b492eb1ec00032be950aa41c5891cea118be2` | `91099076bad166ba0a2c0ce5117523b5b7eb2bc8^..8e5ff927676c7af7816d19a4ba9530efcf461e11` | `78acc17fb71c150cb17bfea4278b00cd4bf0647f^..b96878f3e65049322a60f48aa276a1cd8ca2cf09` |
