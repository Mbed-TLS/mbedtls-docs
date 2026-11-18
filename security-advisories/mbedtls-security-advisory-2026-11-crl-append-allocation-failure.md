# CRL append allocation failure can invalidate trusted revocation state (CVE-2026-90475)

**Title** | CRL append allocation failure can invalidate trusted revocation state
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-90475
**Date** | 16 November 2026
**Affects** | Mbed TLS through 3.6.7; Mbed TLS 4.0.0 through 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions
**Impact** | If an application continues verification after a reported CRL append failure, revoked certificates can be accepted; applications retaining pointers into the cleared CRL can access freed memory
**CWE** | CWE-404: Improper Resource Shutdown or Release; CWE-416: Use After Free; CWE-299: Improper Check for Certificate Revocation
**CAPEC** | CAPEC-114: Authentication Abuse; CAPEC-123: Buffer Manipulation; CAPEC-130: Excessive Allocation
**Severity** | HIGH

## Vulnerability

When an application appends a CRL to a non-empty CRL chain, Mbed TLS allocates
a new list element. If this allocation fails, the parser calls
`mbedtls_x509_crl_free()` on the existing tail element before returning
`MBEDTLS_ERR_X509_ALLOC_FAILED`. This clears the existing element and frees
its dynamically allocated contents even though the caller expects the
previously loaded CRL chain to remain valid.

An application is vulnerable if allocation fails while it appends a CRL and
the application continues to use the modified chain. An adversary may be able
to induce allocation failure by exhausting or nearly exhausting the available
heap. With multiple CRLs, the affected tail is cleared while preceding CRLs
remain available.

Because most fields of `mbedtls_x509_crl` are public, an application may also
retain pointers to data that the failed append frees. Continuing to use such
pointers can result in a use-after-free.

## Impact

`mbedtls_x509_crl_parse_der()` reports the append failure to the caller.
Revoked certificate acceptance can occur only if the application nevertheless
continues certificate verification with the knowingly incomplete CRL chain.
In that case, the vulnerability worsens the incomplete revocation state: in
addition to the new CRL not being loaded, a CRL loaded by a previous successful
call has been cleared.

Certificates revoked by the cleared CRL can then pass verification. Depending
on how the affected application uses certificates, this can permit server
impersonation with a revoked TLS certificate, authentication with a revoked
client certificate, or acceptance of signatures from a revoked certificate.
Revocation protection remains incomplete until the complete CRL chain is
safely reloaded.

Applications that retain pointers into the cleared CRL can access freed
memory, potentially causing memory corruption or other undefined behavior.

## Affected versions

Mbed TLS versions through 3.6.7 are affected.
Mbed TLS versions 4.0.0 through 4.1.1 are affected.
Mbed TLS 4.2.0 is affected.

## Work-around

Applications using an affected version should treat
`MBEDTLS_ERR_X509_ALLOC_FAILED` while parsing or appending a CRL as fatal.
They must not perform certificate verification with the affected chain or use
pointers into it. If processing must continue, discard and safely reload the
complete CRL chain first.

Applications are not affected if they do not append CRLs, or if they stop
using the CRL chain and any pointers into it after an allocation failure.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
Mbed TLS 4.1.2 or a later 4.1.x version, or Mbed TLS 4.3.0 or a later version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if
you are maintaining a branch with backported bug fixes, here are the most
relevant commits. Please note that these commits may not apply cleanly to
older versions of the library, and may not provide a complete fix even if
they do apply. The Mbed TLS development team does not provide support outside
of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | --------------------- |
| Basic fix | 2785e37e5f5a4d1101cead05ffad44b42f0d8023 | 67dd70a6d550f8efad3cf4b9fee5b88a83a903ee | ac49589acb0c4f726e0f0b2408badc0f73781976 |
| With tests and documentation | 2785e37e5f5a4d1101cead05ffad44b42f0d8023^..929f4363a94674c0875e7e716fcf420fb4c8d3c4 | 67dd70a6d550f8efad3cf4b9fee5b88a83a903ee^..71c358f2c805bd35aed2790d18fd8d0d631277e7 | ac49589acb0c4f726e0f0b2408badc0f73781976^..4ef3e573484fb4518739d3824f08ead7aaf1d82b |
