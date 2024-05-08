# Mbed TLS tutorial

The Mbed TLS library is designed to integrate with existing (embedded) applications and to provide the building blocks for secure communication, cryptography and key management. This tutorial helps you understand the steps to undertake.

Mbed TLS is designed to be as loosely coupled as possible, allowing you to only integrate the parts you need without having overhead from the rest. This also results in a very low memory footprint and build footprint for the Mbed TLS library. By eliminating parts you don't need in your system you can get build sizes from as low as 45 kB to a more typical 300 kB for more fully featured setups.

Mbed TLS is designed in the portable C language with embedded environments as a main target and runs on targets as broad as embedded platforms like ARM and AVR to PCs and iPads, iPhones and even the XBox. Please let us know your experiences on other platforms as well.

## The stack

The aim of this tutorial is to show you how to secure your client and server communication with Mbed TLS. The following major components  are involved:

![Mbed TLS Stack.png](https://web.archive.org/web/20210921191453/https://mbed-tls-docs-images.s3.amazonaws.com/mbedtls-stack.png)

From the bottom up:

**Hardware**

The hardware platform provides the physical processor, storage, memory and network interface.

**Operating system**

The operating system provides the Ethernet driver and standard services. Depending on the OS, this includes scheduling, thread-safety and a full network stack.

**Network stack**

Depending on the operating system, the network stack is either fully integrated or is a separate module that provides an abstraction layer from the network interface. The most commonly used are the [lwIP TCP/IP stack](http://savannah.nongnu.org/projects/lwip/) and the [uIP TCP/IP stack](https://www.sics.se/projects/uip-tcpip-connectivity-for-embedded-8-bit-microcontrollers).

**Mbed TLS SSL/TLS library**

Building on top of the network interface, Mbed TLS provides an abstraction layer for secure communication.

**Client application**

The client application uses Mbed TLS to abstract the secure communication from itself.

The steps to integrate Mbed TLS in your application are very dependent on the specific components used above. In this basic tutorial, we assume an operating system with integrated BSD-like TCP/IP stack.

## SSL/TLS

The SSL/TLS part of Mbed TLS provides the means to set up and communicate over a secure communication channel using SSL/TLS.

Its basic functionalities are:

* Initialize an SSL/TLS context.
* Perform an SSL/TLS handshake.
* Send/receive data.
* Notify a peer that a connection is being closed.

Many aspects of such a channel are set through parameters and callback functions:

* The endpoint role: client or server.
* The authentication mode: to state whether certificate verification is needed or not.
* The host-to-host communication channel: send and receive functions.
* The random number generator (RNG) function.
* The ciphers to use for encryption/decryption.
* A certificate verification function.
* Session control: session get and set functions.
* X.509 parameters for certificate handling and key exchange.

Mbed TLS can be used to create an SSL/TLS server and client by providing a framework to set up and communicate through an SSL/TLS communication channel. The SSL/TLS part relies directly on the certificate parsing, symmetric and asymmetric encryption and hashing modules of the library.

## Example client

Let's assume you have a simple network client that tries to open a connection to an HTTP server and read the default page. That application would probably look something like this:

    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <string.h>
    #include <stdio.h>
    #include <netdb.h>

    #define SERVER_PORT 80
    #define SERVER_NAME "localhost"
    #define GET_REQUEST "GET / HTTP/1.0\r\n\r\n"

    int main( void )
    {
        int ret, len, server_fd;
        unsigned char buf[1024];
        struct sockaddr_in server_addr;
        struct hostent *server_host;

        /*
         * Start the connection
         */
        printf( "\n  . Connecting to tcp/%s/%4d...", SERVER_NAME,
                                                     SERVER_PORT );
        fflush( stdout );

        if( ( server_host = gethostbyname( SERVER_NAME ) ) == NULL )
        {
            printf( " failed\n  ! gethostbyname failed\n\n");
            goto exit;
        }

        if( ( server_fd = socket( AF_INET, SOCK_STREAM, IPPROTO_IP) ) < 0 )
        {
            printf( " failed\n  ! socket returned %d\n\n", server_fd );
            goto exit;
        }

        memcpy( (void *) &server_addr.sin_addr,
                (void *) server_host->h_addr,
                         server_host->h_length );

        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons( SERVER_PORT );

        if( ( ret = connect( server_fd, (struct sockaddr *) &server_addr,
                             sizeof( server_addr ) ) ) < 0 )
        {
            printf( " failed\n  ! connect returned %d\n\n", ret );
            goto exit;
        }

        printf( " ok\n" );

        /*
         * Write the GET request
         */
        printf( "  > Write to server:" );
        fflush( stdout );

        len = sprintf( (char *) buf, GET_REQUEST );

        while( ( ret = write( server_fd, buf, len ) ) <= 0 )
        {
            if( ret != 0 )
            {
                printf( " failed\n  ! write returned %d\n\n", ret );
                goto exit;
            }
        }

        len = ret;
        printf( " %d bytes written\n\n%s", len, (char *) buf );

        /*
         * Read the HTTP response
         */
        printf( "  < Read from server:" );
        fflush( stdout );
        do
        {
            len = sizeof( buf ) - 1;
            memset( buf, 0, sizeof( buf ) );
            ret = read( server_fd, buf, len );

            if( ret <= 0 )
            {
                printf( "failed\n  ! ssl_read returned %d\n\n", ret );
                break;
            }

            len = ret;
            printf( " %d bytes read\n\n%s", len, (char *) buf );
        }
        while( 1 );

    exit:

        close( server_fd );

    #ifdef WIN32
        printf( "  + Press Enter to exit this program.\n" );
        fflush( stdout ); getchar();
    #endif

        return( ret );
    }

This is a simple client application that does the following:

* Opens a connection on port 80 to a server-
* Writes a standard HTTP GET request for the main page.
* Reads the result until nothing more is sent.

## Adding secure communication

Adding SSL/TLS to an application requires a number of modifications. The main modifications are setup, configuration and teardown of the SSL contexts and structures. Smaller changes are those made to the network functions for connecting to a server, reading and writing data.

### Setup

Mbed TLS requires a good random number generator and its own SSL context and SSL session store. For random number generation, Mbed TLS contains the CTR_DRBG random number generator, which is used here as well.

The headers required for Mbed TLS:

    #include "mbedtls/net.h"
    #include "mbedtls/ssl.h"
    #include "mbedtls/entropy.h"
    #include "mbedtls/ctr_drbg.h"
    #include "mbedtls/debug.h"

The creation and initialization of the Mbed TLS structures looks as follows:

    mbedtls_net_context server_fd;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_ssl_context ssl;
    mbedtls_ssl_config conf;

    mbedtls_net_init( &server_fd );
    mbedtls_ssl_init( &ssl );
    mbedtls_ssl_config_init( &conf );
    mbedtls_x509_crt_init( &cacert );
    mbedtls_ctr_drbg_init( &ctr_drbg );

    mbedtls_entropy_init( &entropy );
    if( ( ret = mbedtls_ctr_drbg_seed( &ctr_drbg, mbedtls_entropy_func, &entropy,
                               (const unsigned char *) pers,
                               strlen( pers ) ) ) != 0 )
    {
        printf( " failed\n  ! mbedtls_ctr_drbg_seed returned %d\n", ret );
        goto exit;
    }

### SSL Connection

In a generic TCP/IP client application, the application handles the `socket()` and `connect()` calls. Mbed TLS generally abstracts this inside its network layer (`net_sockets.c`). Thus, the following code gets simplified.

    if( ( server_host = gethostbyname( SERVER_NAME ) ) == NULL )
        goto exit;

    if( ( server_fd = socket( AF_INET, SOCK_STREAM, IPPROTO_IP) ) < 0 )
        goto exit;

    memcpy( (void *) &server_addr.sin_addr, (void *) server_host->h_addr,
                     server_host->h_length );

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons( SERVER_PORT );

    if( ( ret = connect( server_fd, (struct sockaddr *) &server_addr,
                         sizeof( server_addr ) ) ) < 0 )
        goto exit;

Starting the actual connection through Mbed TLS is as follows:

    if( ( ret = mbedtls_net_connect( &server_fd, SERVER_NAME,
                                         SERVER_PORT, MBEDTLS_NET_PROTO_TCP ) ) != 0 )
    {
        printf( " failed\n  ! mbedtls_net_connect returned %d\n\n", ret );
        goto exit;
    }

### Configuring SSL/TLS

Now that the low level socket connection is up and running, you need to configure the SSL/TLS layer.

1. Prepare the SSL configuration by setting the endpoint and transport type, and loading reasonable defaults for the security parameters. The endpoint determines if the SSL/TLS layer acts as a server (`MBEDTLS_SSL_IS_SERVER`) or a client (`MBEDTLS_SSL_IS_CLIENT`). The transport type determines if you are using TLS (`MBEDTLS_SSL_TRANSPORT_STREAM`) or DTLS (`MBEDTLS_SSL_TRANSPORT_DATAGRAM`).

    ```
    if( ( ret = mbedtls_ssl_config_defaults( &conf,
                    MBEDTLS_SSL_IS_CLIENT,
                    MBEDTLS_SSL_TRANSPORT_STREAM,
                    MBEDTLS_SSL_PRESET_DEFAULT ) ) != 0 )
    {
        mbedtls_printf( " failed\n  ! mbedtls_ssl_config_defaults returned %d\n\n", ret );
        goto exit;
    }
    ```

2. Set the authentication mode. It determines how strictly the certificates are checked. For this tutorial, we are not checking anything.

    <span class="notes">**Note:**: Do not use this in a full application.</span>

    ```
    mbedtls_ssl_conf_authmode( &conf, MBEDTLS_SSL_VERIFY_NONE );
    ```

3. Set the random engine and debug function. The library needs to know what to use as callback.

    ```
    mbedtls_ssl_conf_rng( &conf, mbedtls_ctr_drbg_random, &ctr_drbg );
    mbedtls_ssl_conf_dbg( &conf, my_debug, stdout );
    ```

4. For the debug function to work, add a debug callback called `my_debug` above our `main()` function.

    ```
    static void my_debug( void *ctx, int level,
                          const char *file, int line, const char *str )
    {
        ((void) level);
        fprintf( (FILE *) ctx, "%s:%04d: %s", file, line, str );
        fflush(  (FILE *) ctx  );
    }
    ```

5. Now that the configuration is ready, set up the SSL context to use it.

    ```
    if( ( ret = mbedtls_ssl_set_hostname( &ssl, "Mbed TLS Server 1" ) ) != 0 )
    {
        mbedtls_printf( " failed\n  ! mbedtls_ssl_set_hostname returned %d\n\n", ret );
        goto exit;
    }
    ```

6. Finally, the SSL context needs to know the input and output functions it needs to use for sending out network traffic.

    ```
    mbedtls_ssl_set_bio( &ssl, &server_fd, mbedtls_net_send, mbedtls_net_recv, NULL );
    ```

### Reading and writing data

After configuring the SSL/TLS layer, you need to actually write and read through it.

For writing to the network layer:

    while( ( ret = write( server_fd, buf, len ) ) <= 0 )

becomes

    while( ( ret = mbedtls_ssl_write( &ssl, buf, len ) ) <= 0 )

For reading from the network layer:

    ret = read( server_fd, buf, len );

becomes

     ret = mbedtls_ssl_read( &ssl, buf, len );

<span class="notes">**Note:**: If `mbedtls_ssl_read()` or `mbedtls_ssl_write()` returns an error, the connection must be closed.

### Teardown

When closing the application you need to close the SSL/TLS connection cleanly and also destroy any SSL/TLS related information. Finally, free the resources allocated.

    close( server_fd );

becomes:

    mbedtls_net_free( &server_fd );
    mbedtls_ssl_free( &ssl );
    mbedtls_ssl_config_free( &conf );
    mbedtls_ctr_drbg_free( &ctr_drbg );
    mbedtls_entropy_free( &entropy );

### Server authentication

A real application needs to properly authenticate the server. For this you need a set of trusted CAs. How to get or choose this set depends on your use case: to connect to a web server, you can use a list provided by a trusted browser vendor; if your client is a device connecting only to a set of servers you control, you may want to be your own CA.

Code-wise, here is what you need to do in order to enable the verification of the server certificate:

    mbedtls_x509_crt cacert;
    const char *cafile = "/path/to/trusted-ca-list.pem";

    mbedtls_x509_crt_init( &cacert );

    if( ( ret = mbedtls_x509_crt_parse_file( &cacert, cafile ) ) != 0 )
    {
        mbedtls_printf( " failed\n  !  mbedtls_x509_crt_parse returned -0x%x\n\n", -ret );
        goto exit;
    }

    mbedtls_ssl_conf_ca_chain( &conf, &cacert, NULL );

    // remove the following line
    // mbedtls_ssl_conf_authmode( &conf, MBEDTLS_SSL_VERIFY_NONE );

## Conclusion

After changing `SERVER_PORT` to `443`, compiling this application and linking it to the Mbed TLS library, you have an application that can talk basic HTTPS to a web server. The final code is available as `ssl_client1.c` in the source code of the library.

<!-- A small tutorial on the workings of SSL, how Mbed TLS works and integrating SSL into a simple client application. add ssl to application, add ssl, polarssl stack, integrate polarssl, integrate ssl, tutorial, stack, portable, explanation, client, server, example, snippet -->
