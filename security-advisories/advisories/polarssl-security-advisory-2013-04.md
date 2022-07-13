# PolarSSL Security Advisory 2013-04

**Title** |  Buffer overflow in ssl_read_record()
---|---
**CVE** |  CVE-2013-5914
**Date** |  1st of October 2013
**Affects** |  PolarSSL versions prior to 1.1.8
**Not affected** |  PolarSSL 1.2.0 and above
**Impact** |  Possible remote exploit
**Exploit** |  Withheld
**Solution** |  Upgrade to PolarSSL 1.1.8, or 1.2.0 and later
**Credits** |  independently found by both TrustInSoft and Paul Brodeur of<br>Leviathan Security Group

When using TLS 1.1, `ssl_read_record()` omits to check the length of the
incoming data. This results in a possible buffer overflow of the receive-
buffer.

Only versions of PolarSSL prior to 1.1.8 are affected.

## Impact

A third party can remotely trigger this buffer overflow by sending a packet
with more data than **SSL_BUFFER_LEN**. This results in `ssl_fetch_input()`
retrieving that amount of data into the input buffer.

## Resolution

Upgrade to PolarSSL version 1.1.8, 1.2.9, 1.3.0 or try to apply the following
patch.



```diff
diff --git a/library/ssl_tls.c b/library/ssl_tls.c
index 27f2172..a5d1cb1 100644
--- a/library/ssl_tls.c
+++ b/library/ssl_tls.c
@@ -1159,7 +1159,7 @@ int ssl_read_record( ssl_context *ssl )
         /*
          * TLS encrypted messages can have up to 256 bytes of padding
          */
-        if( ssl->minor_ver == SSL_MINOR_VERSION_1 &&
+        if( ssl->minor_ver >= SSL_MINOR_VERSION_1 &&
             ssl->in_msglen > ssl->minlen + SSL_MAX_CONTENT_LEN + 256 )
         {
             SSL_DEBUG_MSG( 1, ( "bad message length" ) );
```


## Advice

We strongly advise you to consider upgrading to the 1.3 branch, or otherwise
apply the patch, upgrade to version
[1.1.8](/tech-updates/releases/polarssl-1.1.8-released),
[1.2.9](/tech-updates/releases/polarssl-1.2.9-released) if outside parties are
present or can connect to your network.
