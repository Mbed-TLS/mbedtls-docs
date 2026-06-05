# Security Vulnerability Processes

## Reporting a vulnerability

If you think you have found a security vulnerability in Mbed TLS or in TF-PSA-Crypto, then please send an email to the security team at <mailto:mbed-tls-security@lists.trustedfirmware.org>. For more information on the reporting and disclosure process, please see the [TrustedFirmware.org security incident handling process](https://trusted-firmware-docs.readthedocs.io/en/latest/security_center/incident_handling_process.html). There are some caveats to that process when applied to Mbed TLS and TF-PSA-Crypto, as listed below:

- Mbed TLS and TF-PSA-Crypto currently do not have any registered ESSes and so there is no primary embargo period.
-  Mbed TLS and TF-PSA-Crypto contain strong cryptography software and to comply with export control restrictions, must only distribute software publicly. As a result, security fixes cannot be shared privately with Trusted Stakeholders, although other vulnerability information can be.
- The nature of Mbed TLS and TF-PSA-Crypto often means that security fixes reveal enough information for a skilled attacker to re-construct the originally reported exploit. This combined with the previous caveat means we often expect to have to withhold security fixes until the public disclosure date.
- Mbed TLS and TF-PSA-Crypto are subject to a lot of scrutiny by security researchers who often have their own disclosure timelines when reporting vulnerabilities. As a result, the default 90 days public embargo period may often not apply.

## Bug bounty program

Mbed TLS and TF-PSA-Crypto are part of Arm's Trusted Firmware [bug bounty program](https://app.intigriti.com/programs/arm/trustedfirmware/detail).

Please report your findings either through the bug bounty program, or via the security alias above - but preferably not both, to simplify tracking on our side.

Here are a few differences between those two ways of reporting:
- Only the bug bounty gives out money.
- If you go through the bug bounty program, you abandon control over disclosure, per the program's [terms and conditions](https://kb.intigriti.com/en/articles/5466165-researcher-terms-conditions#h_aa5c8fa808).
- The bug bounty program requires a proof of concept (PoC). Reporting to the alias lets you choose how to establish the report's credibility.
- Reports through the bug bounty program have an intake delay. The alias reaches the developers directly.

## Advisories

Please see [the security advisories page](../security-advisories/index.md) for a complete list of Mbed TLS and TF-PSA-Crypto security advisories.
