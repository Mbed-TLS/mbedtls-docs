# Strict name matching in certificate revocation (CVE-2026-116462)

**Title** | Strict name matching in certificate revocation
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-116462
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS
**Necessary mitigation** | Affected users must apply the changes described under “[Resolution](#resolution)”
**Impact** | Revoked certificates may be accepted
**CWE** | CWE-299: Improper Check for Certificate Revocation; CWE-173: Improper Handling of Alternate Encoding
**CAPEC** | CAPEC-114: Authentication Abuse; CAPEC-267: Leverage Alternate Encoding; CAPEC-80: Using UTF-8 Encoding to Bypass Validation Logic
**Severity** | MEDIUM
**Credits** | Satoru Kanno (GMO CONNECT Inc.)

## Vulnerability

When Mbed TLS matches a name in a certificate, it uses a byte-for-byte comparison, with a case-insensitive comparison for ASCII letters where applicable. The type of string (`PrintableString`, `UTF8String`, etc.) is ignored for this comparison.

This is a departure from the applicable standard, RFC 5280, which requires names to be normalized before comparison. The normalization procedure differs between different kinds of names, but generally includes space compression, Unicode encoding normalization, and case insensitivity for some types of names. When checking whether a certificate matches a requested name, Mbed TLS's strict comparison fails safe: a certificate with a different spelling of the name is rejected.

Mbed TLS supports checking for revoked certificates through a certificate revocation list (CRL). A CRL entry only applies if the name in the issuer field matches the subject name of the certificate authority (CA) that signed the certificate. When checking whether a certificate is revoked, the strict comparison of names is insecure: the revocation may not be effective.

## Impact

A certificate is wrongly accepted if the issuer name in the CRL entry is encoded differently than in the CA certificate. For example, the following are not matched:

* `AUTORITÉ` vs `autorité` (case insensitivity is restricted to ASCII letters);
* `"autorite\u0301"` vs `"autorit\u00e9"` (no Unicode canonicalization);
* `two␣␣words` vs `two␣words` where `␣` is a space (no space folding).

## Affected versions

All versions of Mbed TLS are affected.

## Work-around

Users should ensure that the CA name in a CRL entry uses the same encoding as in the certificates issued by the CA.

## Resolution

Affected users should apply the workaround described above.

## Fix commits

N/A
