# mbed TLS Security Advisory 2015-01

**Title** |  Remote attack on clients using session tickets or SNI
---|---
**CVE** |  CVE-2015-5291
**Date** |  5th of October 2015
**Affects** |  PolarSSL 1.0 and up
**Not affected** |  PolarSSL 1.2.17 and up, mbed TLS 1.3.14 and up, mbed TLS<br>2.1.2 and up and any version with clients not using session tickets nor<br>accepting hostnames from untrusted parties
**Impact** |  Denial of service and possible remote code execution
**Severity** |  High
**Exploit** |  Withheld

PolarSSL versions starting with 1.0 and up to the PolarSSL 1.2.16, mbed TLS
1.3.13 and mbed TLS 2.1.1 releases are affected by a remote attack in their
default configuration in some use cases.

This vulnerability was discovered by [Guido Vranken of
Intelworks](https://guidovranken.wordpress.com/2015/10/07/cve-2015-5291/).

This Security Advisory describes the vulnerability, impact and fix for the
attack.

## Vulnerability

When the client creates its ClientHello message, due to insufficient bounds
checking it can overflow the heap-based buffer containing the message while
writing some extensions. Two extensions in particular could be used by a
remote attacker to trigger the overflow: the session ticket extension and the
server name indication (SNI) extension.

Starting with PolarSSL 1.3.0 which added support for session tickets, any
server the client connects to can send an overlong session ticket which will
cause a buffer overflow if and when the client attempts to resume the
connection with the server. Clients that disabled session tickets or never
attempt to reconnect to a server using a saved session are not vulnerable to
this attack vector.

Starting with PolarSSL 1.0.0, this overflow could also be triggered by an
attacker convincing a client to use an overlong hostname for the SNI
extension. The hostname needs to be almost as long at `SSL_MAX_CONTENT_LEN`,
which as 16KB by default, but could be smaller if a custom configuration is
used. Clients that do not accept hostnames from unstrusted parties are not
vulnerable to this attack vector.

## Impact

Depending on the implementation of the memory allocator, this could result in
a Denial of Service (client crash) or a possible Remote Code Execution.

Servers are not affected in any version.

## Resolution

Upgrade to PolarSSL 1.2.17, mbed TLS 1.3.14 or mbed TLS 2.1.2. If you can't,
use the workaround below.

## Workaround

To be protected against this vulnerability, you need to apply _both_ of the
following work-arounds.

  * Do not use ticket-based session resumption. This can be achieved in two ways: (1) do not attempt to resume a saved session (do not use `mbedtls_get_session()` / `mbedtls_set_session()`), or (2) if you want to resume sessions, make sure you're not using tickets by calling `ssl_set_session_tickets( SSL_SESSION_TICKETS_DISABLED )` in 1.3.x or `mbedtls_ssl_conf_session_tickets( MBEDTLS_SSL_SESSION_TICKETS_DISABLED )` in 2.x

  * If you accept hostnames from unstrusted parties, validate that they are at most 255 bytes long (limit defined by RFC 1305) before passing them to `ssl_set_hostname()`.
