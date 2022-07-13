# PolarSSL Security Advisory 2013-03

**Title** |  Denial of Service through Certificate message during handshake
---|---
**CVE** |  CVE-2013-4623
**Date** |  21th of June 2013
**Affects** |  PolarSSL versions prior to 1.1.7 or 1.2.8
**Not affected** |  PolarSSL Clients / Servers without PEM support<br>(POLARSSL_PEM_C not defined)
**Impact** |  Denial of service through infinite loops
**Exploit** |  Withheld
**Solution** |  Upgrade to PolarSSL 1.1.7 or 1.2.8
**Credits** |  Jack Lloyd [lloyd@randombit.net](mailto:lloyd@randombit.net)

A bug in the logic of the parsing of PEM encoded certificates in
x509parse_crt() can result in an infinite loop, thus hogging processing power.

While parsing a Certificate message during the SSL/TLS handshake, PolarSSL
extracts the presented certificates and sends them on to be parsed. As the RFC
specifies that the certificates in the Certificate message are always X.509
certificates in DER format, bugs in the decoding of PEM certificates should
normally not be triggerable via the SSL/TLS handshake.

Versions of PolarSSL prior to 1.1.7 in the 1.1 branch and prior to 1.2.8 in
the 1.2 branch call the generic `x509parse_crt()` function for parsing during
the handshake. `x509parse_crt()` is a generic functions that wraps parsing of
both PEM-encoded and DER-formatted certificates. As a result it is possible to
craft a Certificate message that includes a PEM encoded certificate in the
Certificate message that triggers the infinite loop.

This bug and code path will only be present if PolarSSL is compiled with the
POLARSSL_PEM_C option. This option is enabled by default.

## Impact

A third party can set up a SSL/TLS handshake with a server and send a
malformed Certificate handshake message that results in an infinite loop for
that connection. With a Man-in-the-Middle attack on a client, a third party
can trigger the same infinite loop on a client.

## Resolution

Upgrade to PolarSSL version 1.1.7 or 1.2.8 or try to apply the following
patch.



```diff
diff --git a/include/polarssl/x509.h b/include/polarssl/x509.h
index 87151c9..296925f 100644
--- a/include/polarssl/x509.h
+++ b/include/polarssl/x509.h
@@ -425,6 +425,18 @@ extern "C" {

 /** \ingroup x509_module */
 /**
+ * \brief          Parse a single DER formatted certificate and add it
+ *                 to the chained list.
+ *
+ * \param chain    points to the start of the chain
+ * \param buf      buffer holding the certificate DER data
+ * \param buflen   size of the buffer
+ *
+ * \return         0 if successful, or a specific X509 or PEM error code
+ */
+int x509parse_crt_der( x509_cert *chain, const unsigned char *buf, size_t buflen );
+
+/**
  * \brief          Parse one or more certificates and add them
  *                 to the chained list. Parses permissively. If some
  *                 certificates can be parsed, the result is the number
diff --git a/library/ssl_tls.c b/library/ssl_tls.c
index 9087ab4..e0cddf8 100644
--- a/library/ssl_tls.c
+++ b/library/ssl_tls.c
@@ -2375,8 +2375,8 @@ int ssl_parse_certificate( ssl_context *ssl )
             return( POLARSSL_ERR_SSL_BAD_HS_CERTIFICATE );
         }

-        ret = x509parse_crt( ssl->session_negotiate->peer_cert, ssl->in_msg + i,
-                             n );
+        ret = x509parse_crt_der( ssl->session_negotiate->peer_cert,
+                                 ssl->in_msg + i, n );
         if( ret != 0 )
         {
             SSL_DEBUG_RET( 1, " x509parse_crt", ret );
```


## Advice

We strongly advise you to consider upgrading to version
[1.1.7](/tech-updates/releases/polarssl-1.1.7-released) or
[1.2.8](/tech-updates/releases/polarssl-1.2.8-released), or apply the provided
path, if outside parties are present or can connect to your network.
