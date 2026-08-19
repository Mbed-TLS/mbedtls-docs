# X.509 CA bit forgery via invalid basicConstraints extension (CVE-2026-49300)

**Title** | X.509 CA bit forgery via invalid basicConstraints extension
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-49300
**Date** | 7th of July, 2026
**Affects** | all versions of Mbed TLS up to 3.6.6; Mbed TLS 4.0.0 to 4.1.0
**Not affected** | Mbed TLS 3.6.7 and later 3.6.x versions; Mbed TLS 4.1.1 and later 4.1.x versions; Mbed TLS 4.2.0 and later 4.x versions
**Impact** | end-entity certificates may be read as CA certificates
**Severity** | HIGH
**Credits** | Mohammad Seet (mhdsait101); Pablo Ruiz García; Felix Graf Lange, Maximilian Radoy, Niklas Niere, Juraj Somorovsky (all Paderborn University), Marcel Maehren and Jörg Schwenk (both Ruhr University Bochum); NVIDIA Project Vanessa

## Vulnerability

Due to two flaws in how Mbed TLS parses X.509 certificates, some technically invalid certificates are parsed as having the CA bit set, while many other X.509 parsers accept these certificates as end-entity (non-CA) certificates.

### Unchecked sequence boundary

According to [RFC 5280 §4.1](https://datatracker.ietf.org/doc/html/rfc5280#section-4.1), each extension in an X.509 certificate is given by an OID, an optional critical flag, and the extension value inside an ASN.1 OCTET STRING. The extension value is itself formatted according to ASN.1 rules. In a basicConstraints extension, the value is a SEQUENCE.

Mbed TLS accepts certificates that are syntactically invalid, where the content of the basicConstraints OCTET STRING is a truncated SEQUENCE, but subsequent bytes of the certificate form a valid SEQUENCE. As a consequence, it is possible to craft an invalid certificate where Mbed TLS parses basicConstraints as a SEQUENCE containing the boolean cA:TRUE, while many major X.509 implementations ignore the invalid extension (and the cA flag defaults to FALSE).

### Invalid CA flag type

According to [RFC 5280 §4.2.1.9](https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.9), the basicConstraints extension in an X.509 certificate is an ASN.1 SEQUENCE which contains an optional boolean (cA flag, defaulting to FALSE) followed by an optional INTEGER (maximum path length). Certificates where the cA flag is absent but the maximum path length is present are syntactically valid, but certificate authorities must not emit such certificates.

For historical reasons, Mbed TLS accepts a variant of the standard encoding where the CA value is an INTEGER. Thus it interprets a basicConstraints extension containing only a nonzero INTEGER as a CA certificate, whereas correct X.509 implementations parse it as having the BOOLEAN cA field omitted (defaulting to FALSE).

## Impact

Each flaw causes some maliciously crafted X.509 certificates to be accepted as CA certificates by Mbed TLS, but as end-entity certificates by most other X.509 implementations.

This is a problem in the following scenario. Suppose a device can be customized with trusted roots for X.509 certificate validation, with an off-device validator that uses a different X.509 implementation. Suppose further that this process allows some users to upload an end-entity certificate for a specific name, but only authenticated administrators may upload a CA certificate.

A malicious user could upload a specially crafted certificate that looks like an end-entity certificate to the off-device validator, but is interpreted as a CA certificate on the device using Mbed TLS. This would allow the user to then authenticate with an arbitrary name, and not just the specific name submitted to the validator.

## Affected versions

All versions of Mbed TLS up to 3.6.6 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.0 are affected.

## Work-around

The vulnerabilities rely on the same certificate being interpreted differently by different TLS implementations. If Mbed TLS is used both to determine which certificates may be registered as trusted roots and to validate the certificate chain, there is no inconsistency.

The vulnerabilities only affect invalid certificates that certificate authorities must not emit. Therefore applications are only affected if they accept certificates directly from untrusted users. Applications are not affected if they require users to submit a certificate signing request (CSR) to a certificate authority (CA), and the application only accepts certificates from a trusted CA.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.7 or a later 3.6.x version,
or to Mbed TLS 4.1.1 or a later 4.1.x version,
or to Mbed TLS 4.2.0 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | --------------------- |
| Basic fix #1 | 07f45b87681c1a0680c260089d3e6349b25fdd08 | 9007fc4b9be08da1d494f8fa4a5a09180291956b | 6c8ae1ea48ffa29d5401171244737eb0bc7f4d9c |
| Basic fix #2 | 4fb9c9e439fd1e7e44697d23d50f00b4642fbe08 | f6afd20e719b6b3a8dcbf28dea3a0f736e9f02a9 | 5cc6fb22c63ecf946920bce3d5185baf03ab9559 |
| Both fixes with tests | aecc26ac7c523e741dd62d94890278326fe7c230..abb6bcd35400128d7d529405369e7592eac73c16 | b2e36d7d7aa9968087eac0a40457783c61c90720..49b13b34b332d997943f7a09dc846a0fa14a5a30 | 4a1d150cdf441d0b1d984ea825a21d5770a9f94a..e31c644041e1bdc021e1c28eb723cb770b4d31b0 |
