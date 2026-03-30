# Risk of insufficient protection of serialized session or context data leading to potential memory safety issues (CVE pending)

**Title** | Risk of insufficient protection of serialized session or context data leading to potential memory safety issues
--------- | ---------------------------------------------------------------------------------------------------------------
**CVE** | Pending
**Date** | 31 March 2026
**Affects** | All Mbed TLS versions supporting session or context serialization
**Severity** | LOW
**Credits** | Haruto Kimura (Stella) and Eva Crystal (0xiviel)

## Vulnerability

Mbed TLS provides APIs allowing applications to serialize and later restore TLS
sessions or contexts. These mechanisms are typically used to implement session
cache, or session resumption. The serialized data is not cryptographically
protected.

These APIs assume that the application ensures the confidentiality and integrity
of serialized data. However, the documentation did not clearly communicate that
failure to protect the integrity of this data may lead not only to authentication
or confidentiality issues, but also to memory safety issues when restoring
corrupted or modified state.

If an application restores TLS state from a serialized buffer that has been
modified or corrupted, the library may process inconsistent or malformed data
structures during deserialization. In certain cases, this may result in
out-of-bounds reads or writes, or other undefined behavior while restoring the
TLS structures.

## Impact

A breach of confidentiality of the serialized data could result in full
compromise of the associated TLS session, including loss of confidentiality and
integrity of past and future application data protected under that session.

A breach of integrity may allow modification of the serialized data prior to
restoration. Since this data is treated as trusted internal state, tampering
may lead to memory safety violations such as out-of-bounds reads or writes,
potentially resulting in crashes or compromise of the application or server
integrity, depending on the environment.

## Affected versions

All versions of Mbed TLS that support TLS session or context serialization may
be affected if serialized data can be accessed or modified by an attacker.

## Workarounds

Applications using TLS serialization APIs must ensure that serialized data is
protected against modification and disclosure.

Recommended measures include:
- Store serialized TLS state only in trusted storage.
- Protect serialized data using cryptographic integrity protection, such as:
  - authenticated encryption (AEAD), or
  - a secure MAC.
- Ensure that serialized TLS data cannot be accessed or modified by untrusted
  parties.
- Validate storage integrity before restoring serialized TLS sessions or
  contexts.

## Additional considerations

Serialized TLS session and context data is only guaranteed to be compatible
when it is restored by a compatible Mbed TLS build.

Applications should assume that serialized formats may change across:
- different Mbed TLS versions, or
- different Mbed TLS compile-time configuration options that affect the
  serialization format.

To detect such mismatches, serialized sessions and contexts include a header
containing the Mbed TLS version and a configuration bitflag describing relevant
compile-time options. This header is checked when loading serialized data.

Nevertheless, serialized data should be treated as ephemeral cache data. In
particular, applications are encouraged to clear any persistent cache when
upgrading Mbed TLS or rebuilding it with different configuration options.

The serialized format itself is independent of the in-memory layout of the C
structures used by the library. Fields are encoded explicitly with defined
sizes and byte order rather than by copying raw structure memory. As a result,
differences in processor architecture, compiler, ABI, or structure packing are
not expected to affect compatibility of serialized data.

The serialized format also does not depend on the application's runtime TLS
configuration. Changes in how the application configures TLS contexts therefore
do not affect the binary format of the serialized data.

## Resolution

No change to the Mbed TLS API is required.

The documentation has been clarified in 3.6.6 and 4.1.0 to explicitly state that
applications must ensure both confidentiality and integrity of serialized TLS
data, and to highlight the potential for memory safety issues if this requirement
is not met.

Users should review their use of TLS session or context serialization and ensure
that serialized data is protected against unauthorized access and modification.
