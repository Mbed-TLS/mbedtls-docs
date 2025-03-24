# Potential authentication bypass in TLS handshake

**Title** | Potential authentication bypass in TLS handshake
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-27810
**Date** | 24 March 2025
**Affects** | All versions of Mbed TLS
**Severity** | MEDIUM

## Vulnerability

During the TLS handshake, the Finished message ensures that the handshake has not been tampered with by an active attacker. If a memory allocation fails or a cryptographic hardware driver returns an error at a specific point during the handshake, the Finished message will be incorrectly calculated to be the contents of uninitialized stack memory.

## Impact

An attacker with the ability to trigger memory allocation failures or cryptographic hardware failures may be able to exploit this to break the security guarantees of the TLS handshake. This may mean that they are able to tamper with the handshake through a Man in the Middle attack or replay handshake messages to impersonate a legitimate peer.

## Affected versions

All versions of Mbed TLS up to 2.28.9 and all versions of Mbed TLS 3.x up to 3.6.2 are affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.3 or Mbed TLS 2.28.10

## Work-around

Ensure that enough memory is available before performing a handshake and that any cryptographic hardware drivers used for hash functions cannot return errors.
