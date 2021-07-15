# PolarSSL Security Advisory 2014-04

**Title** |  Remote attack using crafted certificates
---|---
**CVE** |  CVE-2015-1182
**Date** |  19th of January 2015
**Affects** |  PolarSSL 1.0 and up
**Not affected** |  mbed TLS 1.3.10 and up, PolarSSL 1.2.13 and up and any
version with servers not asking for client certificates
**Impact** |  Denial of service and possible remote code execution
**Severity** |  High
**Exploit** |  Withheld

PolarSSL versions starting with 1.0 and up to the PolarSSL 1.3.9 and PolarSSL
1.2.12 are affected by a remote attack in some configurations.

This vulnerability was internally discovered using the Codenomicon Defensics
test suite and reported externally by [Certified
Secure](https://www.certifiedsecure.com/polarssl-advisory).

This Security Advisory describes the vulnerability, impact and fix for the
attack.

## Vulnerability

During the parsing of a ASN.1 sequence, a pointer in the linked list of
`asn1_sequence` is not initialized by `asn1_get_sequence_of()`. In case an
error occurs during parsing of the list, a situation is created where the
uninitialized pointer is passed to `polarssl_free()`.

This sequence can be triggered when a PolarSSL entity is parsing a
certificate. So practically this means clients when receiving a certificate
from the server or servers in case they are actively asking for a client
certificate.

## Impact

Depending on the attackers knowledge of the system under attack, this results
at the lowest into a Denial of Service, and at the most a possible Remote Code
Execution.

## Fix

The fix is a one-line addition to _asn1parse.c_ :



    diff --git a/library/asn1parse.c b/library/asn1parse.c
    index a3a2b56..e2117bf 100644
    --- a/library/asn1parse.c
    +++ b/library/asn1parse.c
    @@ -278,6 +278,8 @@ int asn1_get_sequence_of( unsigned char **p,
                 if( cur->next == NULL )
                     return( POLARSSL_ERR_ASN1_MALLOC_FAILED );

    +            memset( cur->next, 0, sizeof( asn1_sequence ) );
    +
                 cur = cur->next;
             }
         }


## Workaround and resolution

Apply the above patch to your codebase, or download and use mbed TLS 1.3.10 or
PolarSSL 1.2.13.
