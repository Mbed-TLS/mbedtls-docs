# Is Mbed TLS FIPS certified?

## What is FIPS certification
When we refer to FIPS certification for cryptographic software, we actually mean FIPS PUB 140-2.

To coordinate the requirements and standards for cryptographic modules, the National Institute of Standards and Technology (NIST) issued the high-level FIPS 140 Publication Series.

The FIPS 140-2 standard is an official security accreditation program for cryptographic modules. As a private party, we can have our products certified for use in government departments and regulated industries.

When a software or hardware product has been tested and validated, it receives a FIPS 140-2 certificate that specifies the exact module name and version numbers. This information can then be used by third parties to confirm that software has been validated.

## FIPS certification
While the Mbed TLS library is not FIPS certified, a number of the NIST approved test vectors have been incorporated, taking us an important step towards FIPS certification.

## FIPS test vectors
For a FIPS certification, cryptographic modules are normally tested against the Security Requirements for Cryptographic Modules requirements found in the FIPS PUB 140-2.

These requirements include official NIST validating and test vectors for the algorithms. These are included and used in our test suite.

The test suite that is located at `tests/` within the Mbed TLS source code often contains a subset of the available NIST test vectors. So, whenever you run the tests with `make check`, these tests will be run as well.

<!--", is-mbedtls-fips-certified,"Describes the FIPS 140-2 certification and the current status of Mbed TLS certification and presence of the validation and test vectors","NIST, FIPS, FIPS 140-2, 140-2, test vectors, validation vectors, cavp","nist, fips, test vectors, validation, cavp, certification, test suite, accreditation, security",published,"2013-06-25 08:56:00",1,7684,"2015-07-24 11:39:00","Paul Bakker"-->
