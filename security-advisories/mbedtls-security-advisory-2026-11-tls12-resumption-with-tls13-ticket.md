# Client impersonation using a TLS 1.3 ticket in TLS 1.2 session resumption (CVE-2026-93831)

**Title** | Client impersonation using a TLS 1.3 ticket in TLS 1.2 session resumption
--------- | -------------------------------------------------------------------------
**CVE** | CVE-2026-93831
**Date** | 16 November 2026
**Affects** | Mbed TLS 3.3.0 up to and including 3.6.7; Mbed TLS 4.0.0 up to and including 4.1.1; Mbed TLS 4.2.0
**Impact** | Client impersonation and loss of confidentiality and integrity for the maliciously resumed connection
**CWE** | CWE-290: Authentication Bypass by Spoofing; CWE-1288: Improper Validation of Consistency within Input
**CAPEC** | CAPEC-94: Adversary in the Middle (AiTM); CAPEC-272: Protocol Manipulation
**Severity** | HIGH
**Credits** | k01n; Ada Logics in collaboration with Anthropic; Mohammad Seet and Rayan Al Garni; Seungheon Oh; MiniMax M3.1-Flash (M31Flash); Matthew Sanders (Cosmic Canopy LLC, Kama)

## Vulnerability

When a TLS 1.2-capable Mbed TLS server receives a TLS 1.3 session ticket in the
SessionTicket extension of a TLS 1.2 ClientHello, it does not check that the
protocol version stored in the ticket is TLS 1.2. The server accepts the TLS 1.3
ticket and proceeds with TLS 1.2 session resumption. In the common scenario, the
same server supports TLS 1.3 and issued the ticket during a previous TLS 1.3
connection.

In affected versions, a deserialized TLS 1.3 session contains a TLS 1.3
resumption key but no TLS 1.2 master secret. The TLS 1.2 resumption path
therefore uses an all-zero master secret. The attacker can calculate the
record-protection keys and Finished message needed to complete the handshake.
Because resumed TLS 1.2 handshakes skip certificate-based client
authentication, the server completes the handshake without authenticating the
peer.

## Impact

TLS 1.3 session tickets are sent as cleartext PSK identities when a client
attempts to resume a TLS 1.3 session. An attacker who observes such an attempt
can capture a still-valid ticket and replay it in a TLS 1.2 ClientHello.

The attacker can then complete a resumed TLS 1.2 handshake without possessing
the corresponding TLS 1.3 resumption key or an accepted client certificate.
The maliciously resumed connection does not provide the confidentiality or
integrity guarantees expected of TLS because its traffic keys can be calculated
from public information.

If the TLS 1.2 server is configured to authenticate clients and the application
relies solely on the successful establishment of a TLS connection for client
authentication, the attacker may be able to impersonate a legitimate client.

Finally, if the application provides its own implementation of session ticket
handling via the `mbedtls_ssl_ticket_write_t` and `mbedtls_ssl_ticket_parse_t`
callbacks and encodes additional application-level information in tickets
beyond the negotiated TLS session parameters and client identity (for example,
authorization state or access rights), an attacker able to complete the resumed
handshake described above may inherit the same application-level privileges as
the legitimate client whose ticket was used.

## Affected versions

Mbed TLS versions 3.3.0 up to and including 3.6.7, Mbed TLS 4.0.0 up to and
including 4.1.1, and Mbed TLS 4.2.0.

## Work-around

In the most common client-impersonation scenario, an application operating an
Mbed TLS server is affected when all of the following conditions are met:

* The server supports both TLS 1.2 and TLS 1.3, and allows TLS 1.2 session
  resumption through tickets.
* The `MBEDTLS_SSL_SESSION_TICKETS` configuration option is enabled, ticket
  write and parse callbacks are configured with
  `mbedtls_ssl_conf_session_tickets_cb()`, and the configured TLS 1.3
  NewSessionTicket count is nonzero.
* The server is configured to authenticate clients, and the application relies
  on the TLS connection for client authentication.

Applications can mitigate the issue by configuring the server to support only
one protocol version. If TLS 1.3 support is disabled, already issued TLS 1.3
tickets must also be invalidated by resetting the ticket-handling context and
keys.

Alternatively, applications can disable both TLS 1.2 and TLS 1.3 session
tickets. This can be done at build time by disabling the
`MBEDTLS_SSL_SESSION_TICKETS` configuration option, or when setting up the SSL
configuration by not installing ticket callbacks with
`mbedtls_ssl_conf_session_tickets_cb()`. TLS 1.2 session resumption through the
session cache does not use the vulnerable path and can remain enabled.

If support for both protocol versions and TLS 1.2 ticket acceptance must remain
enabled, TLS 1.3 ticket generation can be stopped by configuring the server to
send zero NewSessionTicket messages using
`mbedtls_ssl_conf_new_session_tickets()`. Already issued TLS 1.3 tickets must
also be invalidated by resetting the ticket-handling context and keys.

Note that, if the TLS 1.2 server accepts tickets issued by other TLS 1.3 virtual
hosts or server instances, ticket generation must also be stopped at those
sources, and all TLS 1.2 servers accepting their tickets must reject previously
issued tickets.

As a separate mitigation for client impersonation, applications can
independently authenticate and authorize the peer at the application layer
after every TLS connection, without relying on identity or authorization state
restored from the session ticket.

## Resolution

Affected users of the 3.6 LTS branch should upgrade to 3.6.8 or later.
Affected users of the 4.1 LTS branch should upgrade to 4.1.2 or later.
Affected users of the 4.x series should upgrade to 4.3.0 or later.

The fix rejects tickets whose stored protocol version is not TLS 1.2 before
entering TLS 1.2 session resumption. As defense in depth, TLS 1.2 master secrets
and TLS 1.3 resumption keys now occupy the same session-secret storage so that
neither remains all-zero if a cross-version ticket acceptance bug is introduced
in the future.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you
are maintaining a branch with backported bug fixes, here are the most relevant
commits. Please note that these commits may not apply cleanly to older versions
of the library, and may not provide a complete fix even if they do apply. The
Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | --------------------- |
| Basic fix | f5b061d61c13b53484b1baedafe40564443a3942^..524256bf4bfa95523cb320a0476d3e5e6f06c81b | dc38273c0578195cfbfa98ca30ffc14e393c55dd^..afd71ad3555d3c5c986fc96579572075729a9608 | e32e49ecc1e6b67cfb90c2241bd7b695507b1916^..3733e82170be389dacbd9e8c2a1b0b8e16aa8f36 |
| With defense in depth, tests and documentation | f5b061d61c13b53484b1baedafe40564443a3942^..4b753049f16b228fb40acb4abcce168e9963e6b7 | dc38273c0578195cfbfa98ca30ffc14e393c55dd^..ad5a47077c8e14491e2ec4a0df816c14a5066a51 | e32e49ecc1e6b67cfb90c2241bd7b695507b1916^..1f7bb8d3a3beb507b8a215ac568b707b3ea0c5e5 |
