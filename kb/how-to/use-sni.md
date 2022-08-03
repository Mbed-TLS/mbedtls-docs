## How to use Server Name Indication

Server Name Indication (SNI) is defined in [RFC 6066](https://tools.ietf.org/html/rfc6066). It is one of many TLS extensions, and an unofficial but accepted standard on the Internet.

### Why is SNI useful?

When several virtual servers are running on the same host with the same IP address but have different domain names with corresponding certificates, the host has no way of knowing which virtual server certificate to send during a handshake. This is because the peers only send application layer data like domain names after the TLS handshake finishes.

One possible solution would be to have the virtual servers share a certificate. A more maintainable and flexible solution is to perform the handshake using the SNI Extension, which lets the server know the DNS hostname(s) of the target virtual server. This allows the server to respond with a server-specific certificate.

### Enabling the SNI extension

SNI is enabled in the default configuration.

**SNI requires X509 certificates**, so the first step is to enable X509 in your Mbed TLS `config.h` file:
```
    ./scripts/config.pl set MBEDTLS_X509_CRT_PARSE_C
    ./scripts/config.pl set MBEDTLS_SSL_SERVER_NAME_INDICATION
```
These are usual Mbed TLS compile time options, so you need to set them before compiling the library. For more information on configuring Mbed TLS please visit this [knowledge base article](https://tls.mbed.org/kb/compiling-and-building/how-do-i-configure-mbedtls).

### Configuring the SNI extension

You need to configure SNI on both the [client side](#client-side) and the [server side](#server-side).

#### Client side

The SNI extension uses the same server name that the client uses to verify the server certificates during the handshake. You can set it in the same [function](https://tls.mbed.org/api/ssl_8h.html):
```
    mbedtls_ssl_set_hostname( context, "virtualserver15.myhost.com" );
```
<span class="warnings">**Warning:** If the hostname is not set with this function, Mbed TLS will silently skip certificate verification entirely. Always set the hostname with this function - even when not using SNI!</span>

#### Server side

Mbed TLS provides a very flexible solution for selecting the right certificate. The server application developer has to implement and set a callback function that:
1. Receives the server name and a pointer to the SSL context as a parameter.
1. Uses any means available in its environment to choose the appropriate certificate.
1. Sets the certificate in the SSL context.

**Example:**

The sample application `programs/ssl/ssl_server2.c` does this as follows:
```
    int sni_callback( void *p_info, mbedtls_ssl_context *ssl,
                  const unsigned char *name, size_t name_len )
    {
        const sni_entry *cur = (const sni_entry *) p_info;

        /* traverse the certificate info list */
        while( cur != NULL )
        {
            /* find the one with the name requested */
            if( name_len == strlen( cur->name ) &&
                memcmp( name, cur->name, name_len ) == 0 )
            {
                /* set the corresponding CA if applicable */
                if( cur->ca != NULL )
                    mbedtls_ssl_set_hs_ca_chain( ssl, cur->ca, cur->crl );

                /* set the authentication mode if it differs from the default */
                if( cur->authmode != DFL_AUTH_MODE )
                     mbedtls_ssl_set_hs_authmode( ssl, cur->authmode );

                /* set the certificate in the context */
                return( mbedtls_ssl_set_hs_own_cert( ssl, cur->cert, cur->key ) );
            }

            /* step to the next certificate info in the list */
            cur = cur->next;
        }

        /* certificate not found: return an error code */
        return( -1 );
    }
```
Here the pointer `p_info` points to a structure with sextuples of `<name, certificate, certificate authority, certificate revocation list, authentication mode>`, but it may change depending on the needs of a particular application.

To enable Mbed TLS using the callback function, you also have to register it:
```
    mbedtls_ssl_conf_sni( &conf, sni_callback, sni_info );
```
Here `conf` is an `mbedtls_ssl_config` structure, and the framework will pass `sni_info` to the callback function as the first parameter. Please make sure that the structure `sni_info` points to is properly initialised before calling this function, and stays consistent with the application's needs during the SSL context lifetime.

### Special situations

Sometimes certificates are issued for IP addresses and not DNS names. Unfortunately, Mbed TLS doesn't yet support using such certificates while SNI is turned on. This means that you may be able to set IP addresses with the `mbedtls_ssl_set_hostname` function, but it will result in non-compliant behavior and limited functionality.

As mentioned above, Mbed TLS uses the same function to set the name for the certificate verification and to set the name for the SNI. The standard does not allow sending IP addresses in the SNI extension, and using an IP address when the SNI is turned on means that a compliant server can't possibly find the matching certificate, and some servers may terminate the connection immediately.

<span class="notes">**Note:** When SNI is turned off, Mbed TLS can handle certificates that have IP addresses as their subject name or subject alternative name.</span>

<!---",use-sni,"sni, server name indication, virtual host, rfc 6066, tls extension",,,published,"2016-07-05 14:55:00",2,4773,"2016-07-06 12:55:00","Janos Follath"--->
