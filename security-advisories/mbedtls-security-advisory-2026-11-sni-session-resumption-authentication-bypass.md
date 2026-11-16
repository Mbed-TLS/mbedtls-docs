# Client-authentication bypass through cross-SNI session resumption (CVE-2026-93776)

**Title** | Client-authentication bypass through cross-SNI session resumption
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-93776
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; Mbed TLS 4.0.0-beta through 4.1.1; Mbed TLS 4.2.0
**Fix versions** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later
**Necessary mitigation** | Affected applications must also apply the changes described under “[Resolution](#resolution)”
**Impact** | A remote client can bypass a virtual host's client-certificate authentication requirement
**CWE** | CWE-287: Improper Authentication
**CAPEC** | CAPEC-115: Authentication Bypass
**Severity** | HIGH
**Credits** | Younghyo Cho, CIS Lab, Seoultech; Jaehun Lee, Pohang University of Science and Technology (POSTECH); Bhabani Sankar Das; Shuaigangran Yue (Southeast University, QAX corp.) and Han Qiu (Southeast University)

## Vulnerability

An Mbed TLS server can use Server Name Indication (SNI) to host several virtual
hosts with different client-authentication policies. For example, its SNI
callback can select `MBEDTLS_SSL_VERIFY_OPTIONAL` for `public.example` and
`MBEDTLS_SSL_VERIFY_REQUIRED` for `admin.example`, using
`mbedtls_ssl_set_hs_authmode()`.

If these virtual hosts share a session cache or session-ticket keys, a client
can establish a resumable session with `public.example` without presenting a
client certificate, then request resumption of that session while specifying
`admin.example` in SNI. The server agrees to resume the session without
performing the certificate authentication required by the second virtual host.
Selecting `MBEDTLS_SSL_VERIFY_REQUIRED` in the SNI callback does not cause the
resumed handshake to authenticate the client under the new policy.

The issue affects TLS 1.2 session ID-based resumption and session tickets, and
TLS 1.3 session tickets.

Applications are vulnerable when they accept session resumption across virtual
hosts with different client-authentication policies and rely on the TLS
handshake to enforce those policies. This includes a virtual host that requires
a client certificate sharing resumption state with one that permits a
connection without a client certificate.

## Impact

A remote attacker who can obtain a resumable session from a less restrictive
virtual host can connect to a protected virtual host without satisfying its
client-certificate authentication requirement. This can allow unauthorized
access to application data or operations protected by that requirement.

## Affected versions

All versions of Mbed TLS up to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0-beta to 4.1.1 are affected.
Mbed TLS 4.2.0 is affected.

Upgrading the library alone does not protect an application that continues to
share resumption state across different client-authentication policies.

## Work-around

Use separate SSL configurations with independent session caches
and independent ticket keys for virtual hosts with different client
authentication policies. The application must be able to select the appropriate
configuration before the TLS handshake using information available outside TLS,
such as the listening address or port.

If the application must support virtual hosts with different client-authentication
policies but cannot distinguish between them before the TLS handshake, do not
enable session ID-based resumption or session tickets on the shared server
configuration: do not register session-cache callbacks through
`mbedtls_ssl_conf_session_cache()` or ticket callbacks through
`mbedtls_ssl_conf_session_tickets_cb()`. Both resumption mechanisms must remain
disabled.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
Mbed TLS 4.1.2 or a later 4.1.x version, or Mbed TLS 4.3.0 or a later 4.x version,
and update their server applications to isolate resumption state.

The fix adds `mbedtls_ssl_set_hs_session_cache_context()` and
`mbedtls_ssl_set_hs_session_ticket_context()` APIs. An application's SNI
callback must use these functions to select independent cache and ticket
contexts for virtual hosts with different client-authentication policies.

The library fix also ensures that TLS 1.2 session tickets are processed after
the SNI callback, regardless of the ordering of the ClientHello extensions.
The `ssl_server2` example is updated to select separate cache and ticket contexts
for each configured SNI hostname.

Applications must reset the corresponding session cache and invalidate
previously issued tickets when the associated client-authentication policy
changes. When deploying this mitigation, discard any previously shared cached
sessions and replace the shared ticket keys.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you
are maintaining a branch with backported bug fixes, here are the most relevant
commits. Please note that these commits may not apply cleanly to older versions
 of the library, and may not provide a complete fix even if they do apply. The
Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | -------------------- |
| Basic fix | 5df267d759d6442246b5ebe5033ed7c814726eb5^..602b8b78bd5d3c29d0a7888172fb761573c82d1e f7c0bfd9e53a3433ada9e5a7c30abfb3c3b79e7a 67098ff9d5db38c7ad0aff1980abb8f9805bdcb5^..b102d4d5534cf129af88e764570b3ebc9119882d | cc6ece1de8566d3438812777aef73c30ed7a4eaa^..2f9bf7b566beebb786ba550826142f6d8743f741 5351c70baf1921d1d2405663888cced416a3772d 3cb187071d9ded0220cfc04d3a1335241fc8b08a^..e2fd3fcd98c23cb243fbf228cad5df93a9df8ff1 | 8f6adda3c16dac6f208f2484f4dd5917bd54b4d6^..2f563dadb1d30137ed10b0fe2a24ade9357af2f7 d8e6261d43713add83eb15e2e0627eec487ac954 45289be141b6b25c7dcdf846a2088847d4e01617^..a1eea0b325ca462d6eb5a5f53eea2709bc030c08 |
| With tests and documentation | 5df267d759d6442246b5ebe5033ed7c814726eb5^..cbf9d3b7270d5743f793a8c2f6f8308043cec255 | cc6ece1de8566d3438812777aef73c30ed7a4eaa^..506ede63b56e84092a34427692340e0157ce028a | 8f6adda3c16dac6f208f2484f4dd5917bd54b4d6^..9ab2af778548328991dfe16a7134cafe4ae9dbde |
