# PolarSSL Security Advisory 2011-02

**Title** |  Weak random number generation within virtualized environments
---|---
**CVE** |  CVE-2011-4574
**Date** |  15th of December 2011
**Affects** |  All version of PolarSSL prior to 1.1.0
**Not affected** |  Instances not running in virtualized environments
**Impact** |  Key retrieval possible
**Exploit** |  Withheld
**Solution** |  Upgrade to PolarSSL 1.1.0 and move to CTR_DRBG random
generator
**Workaround** |  Provide another random source to the SSL layer
**Credits** |  Jacob Appelbaum, Marsh Ray, and Oscar Koeroo

Feedback from the security community has triggered an investigation into the
quality of PolarSSL's random number generation within virtualized
environments.

PolarSSL versions prior to v1.1 use the
[HAVEGE](http://www.irisa.fr/caps/projects/hipsor/publi.php) random number
generation algorithm. At its heart, this uses timing information based on the
processor's high resolution timer (the RDTSC instruction). This instruction
can be virtualized, and some virtual machine hosts have chosen to disable this
instruction, returning 0s or predictable results.

Further concerns have been raised on the HAVEGE implementation's sole
dependence on timing data.

## Impact

This issue affects machines running within environments where the RDTSC call
has been disabled or handicapped. Currently, the problem seems to be limited
to some commercial cloud server providers.

If affected, this means the RNG produces predictable random and as such
security is severely compromised.

## Resolution

PolarSSL version 1.1.0 contains a new random number generator based on the
CTR_DRBG algorithm specified in [NIST-
SP800-90](http://csrc.nist.gov/publications/nistpubs/800-90A/SP800-90A.pdf).
The entropy used by this algorithm is accumulated from multiple sources,
including the existing HAVEGE RNG, platform-specific entropy sources and
timing sources. This increases the quality of the entropy pool, and makes it
less vulnerable to problems within a single source.

## Advice

We advise everyone to move to the new CTR_DRBG algorithm and entropy pool if
possible.

### Like this?

**Section:**
Security Advisories

**Author:**
Paul Bakker

**Published:**
Oct 14, 2012

**Last updated:**
Jul 12, 2013