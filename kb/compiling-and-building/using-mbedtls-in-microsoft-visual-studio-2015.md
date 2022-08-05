# Arm Mbed TLS in Microsoft Visual Studio 2015

This tutorial shows how to get started with the Mbed TLS cryptography library in a Windows environment, using Microsoft Visual Studio 2015. This tutorial uses the sample client application (from [this example](https://tls.mbed.org/kb/how-to/mbedtls-tutorial)). This application sends an HTTP request to read an HTML page from a server.This tutorial uses Mbed TLS to enable encrypting our communication with the server with TLS. Note that Mbed TLS supports Visual Studio starting from version 2010.

There are two possible ways to build Mbed TLS on Windows:

- Using the solution file supplied with the Mbed TLS source code.
- Using `cmake` to generate a Visual Studio solution file.

This step-by-step tutorial shows you how to set up Visual Studio for Mbed TLS and the sample application. It assumes that you have already installed Visual Studio for C++. If generating a solution file using `cmake`, you should also install CMake. We tested this tutorial with `cmake` version 3.10.1.

The sample application is a command-line program, written in C. You can just as easily integrate Mbed TLS in any C or C++ application, with or without a (graphical) user interface.

## Download Mbed TLS

First, you need to get the Mbed TLS source code. Download `mbedtls-<version\>-gpl.tgz` from [the Mbed TLS dowload location](https://tls.mbed.org/download). To unpack this file, you can use a tool like [7-zip](http://www.7-zip.org/).

The default installation of Visual Studio creates this folder: My Documents\Visual Studio 2015\Projects. Extract the contents of the .tgz file to this location. Make sure to extract the second occurrence of the `mbedtls-<version>` folder. Otherwise, the paths given later in this tutorial won't match.

<span class="notes">**Note:** You can extract the contents to any location you want, but for the purpose of this tutorial, the download location is the Visual Studio projects folder.</span>

## Use the solution file supplied with the Mbed TLS source code

### Open the Visual Studio solution

You now have this folder: My Documents\Visual Studio 2015\Projects\mbedtls-<version\>\visualc\VS2010.

In this folder, you can find the file `mbedTLS.sln`. This is a Visual Studio `solution` file, which holds all the components Mbed TLS consists of and the rules to build the Mbed TLS library.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-1.png)</span>

Double click the .sln file to open Visual Studio.

On first use, you are asked to upgrade the compiler and libraries because the supplied libraries are for Visual Studio 2010. Select **OK**.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-2.png)</span>

Once opened, you can find all the Visual Studio projects in the solution.

### Build

When Visual Studio opens, it shows all the components of the Mbed TLS source code. For this step, you only need the `mbedTLS` project (shown in bold to indicate that it is the default project), which builds the `mbedTLS` library file. Later, you will link to this library file from the sample application.

Now you can build the library. Because you won't be debugging Mbed TLS, build the `Release` version. To do this, select the `release` configuration in the icon bar. Then press **ctrl+shift+b** to start the building process.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-3.png)</span>

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-4.png)</span>

Not all components may have built successfully. This does not matter as long as the `mbedTLS` project built. Check this by looking in this folder: My Documents\Visual Studio 2015\Projects\mbedtls-<version\>\visualc\VS2010\Release. The file `mbedTLS.lib` msut be present.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-5.png)</span>

### Set up a new project

Now you are ready to set up the sample project. Close the current solution by clicking on **Close solution** in the file menu.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-6.png)</span>

Create a new project by selecting the menu command: **File / New / Project** (or use the **New** icon).

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-7.png)</span>

Visual Studio then asks what kind of project you would like to create. Choose **Empty project**. Type the name of the project, for example `Mbed\_client\_demo`. Check that you have selected the `My Documents\Visual Studio 2015\Projects` folder as the location (the same base path as used for Mbed TLS). Leave the **create directory for solution** checkbox enabled. After you click the **OK** button, you have a new, empty, project.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-8.png)</span>

### Copy sample application

To create an application, you must add a source file. In the solution explorer, right click on **Source files**, and select **Add / New item**.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-9.png)</span>

Visual Studio asks what kind of item you would like to create. Select **C++ file**. Enter a name for the file, for example `client.c`. Click on **Add**.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-10.png)</span>

Copy and paste this piece of code to the new file, and save it:

```
	#include <sys/types.h>

	#ifdef _WIN32
	#include <winsock.h>
	#else
	#include <sys/socket.h>
	#include <netinet/in.h>
	#include <arpa/inet.h>
	#include <netdb.h>
	#endif

	#include <string.h>
	#include <stdio.h>

	#define SERVER_PORT 80
	#define SERVER_NAME "www.google.com"
	#define GET_REQUEST "GET / HTTP/1.0\r\n\r\n"

	int main( void )
	{
	    int ret = 0, len, server_fd = 0;
	    unsigned char buf[1024];
	    struct sockaddr_in server_addr;
	    struct hostent *server_host;

	#ifdef _WIN32
		WSADATA wsaData;
	#endif

	#ifdef _WIN32
	    /*
	     * Init WSA
	     */
	    if( WSAStartup(MAKEWORD(2, 0), &wsaData ) != 0 )
        {
            printf( " WSAStartup() failed\n" );
            goto exit;
        }
	#endif

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

	    len = snprintf((char *)buf, sizeof(buf), GET_REQUEST);

	#ifdef _WIN32
	    while( ( ret = send( server_fd, (char *) buf, len, 0 ) ) <= 0 )
	#else
	    while( ( ret = write( server_fd, buf, len ) ) <= 0 )
	#endif
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
	#ifdef _WIN32
		ret = recv( server_fd, (char *) buf, len, 0 );
	#else
		ret = read( server_fd, buf, len );
	#endif

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

	#ifdef _WIN32
	    if( server_fd )
		closesocket( server_fd );
	    WSACleanup();
	#else
		close( server_fd );
	#endif

	#ifdef _WIN32
	    printf( "  + Press Enter to exit this program.\n" );
	    fflush( stdout ); getchar();
	#endif

	    return( ret );
	}
```

### Compile and test

Before building the new project, you need to add one project setting. In the solution explorer, right click on the project name, in this case **Mbed\_client\_demo**. Select **Properties**.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-11.png)</span>

In the properties dialog, select **Linker / Input**. Select **Additional dependencies**. Click on the down arrow, and choose **edit**.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-12.png)</span>

Type `wsock32.lib` in the dialog, and click on **OK** twice. You need to add this library to the project because line 4 of the source code includes the `winsock` header file. Visual Studio needs to know where to find the executable code for this file.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-13.png)</span>

You can now build the sample application. Press **ctrl+shift+b**. Visual Studio shows `Build: 1 succeeded` in the output screen.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-14.png)</span>

Start the application by pressing the **F5** key. Note that line 16 of the source code states that the application loads the home page of a well-known search engine.

The application shows a command screen, stating that a connection has been made to the server and shows the server's response. Press **enter** to close the application.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-15.png)</span>

To connect to the server using HTTPS, change line 15 to:

```
#define SERVER_PORT 443
```

Build (**ctrl+shift+b**), and run (**F5**) the application again. The application shows an error. You first need to set up a TLS connection. That is what Mbed TLS is for.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-16.png)</span>

### TLS explanation

The TLS part of Mbed TLS provides the means to set up and communicate over a secure communication channel using TLS. Its basic provisions are:

- Initialize a TLS context.
- Perform a TLS handshake.
- Send and receive data.
- Notify a peer that a connection is being closed.

Many aspects of such a channel are set through parameters and callback functions:

- The endpoint role: client or server.
- The authentication mode: whether certificate verification should take place.
- The host-to-host communication channel: send and receive functions.
- The random number generator (RNG) function.
- The ciphers to use for encryption and decryption.
- A certificate verification function.
- Session control: session get and set functions.
- X.509 parameters for certificate-handling and key exchange.

You can use Mbed TLS to create a TLS server and client by providing a framework to set up and communicate through a TLS communication channel. The TLS part relies directly on the certificate parsing, symmetric and asymmetric encryption and hashing modules of the library.

### Modify application to use TLS

[This tutorial](https://tls.mbed.org/kb/how-to/mbedtls-tutorial) describes how to add Mbed TLS to the sample application. For now, replace the code in the `client.c` file by copying and pasting this code over the existing code:

```
#include <string.h>
#include <stdio.h>

/*
* Include mbedtls
*/
#include "mbedtls/net.h"
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

#define SERVER_PORT "443"
#define SERVER_NAME "www.google.com"
#define GET_REQUEST "GET / HTTP/1.0\r\n\r\n"

#define DEBUG_LEVEL 1

void my_debug(void *ctx, int level, const char *str)
{
	if (level < DEBUG_LEVEL)
	{
		fprintf((FILE *)ctx, "%s", str);
		fflush((FILE *)ctx);
	}
}

int main(void)
{
	int ret = 0, len;
	unsigned char buf[1024];
	mbedtls_net_context server_fd;

	/*
	* Init mbedtls
	*/
	mbedtls_entropy_context entropy;
	mbedtls_ctr_drbg_context ctr_drbg;
	mbedtls_ssl_context ssl;
	mbedtls_ssl_config conf;
	char *pers = "mbedtls_ssl_example";

	mbedtls_net_init( &server_fd );
	mbedtls_ctr_drbg_init( &ctr_drbg );

	/*
	* Seed the Random Number Generator
	*/
	printf( "\n  . Seeding the random number generator..." );
	fflush( stdout );

	mbedtls_entropy_init( &entropy );
	if( ( ret = mbedtls_ctr_drbg_seed( &ctr_drbg, mbedtls_entropy_func, &entropy,
		( const unsigned char * )pers,
		strlen( pers ) ) ) != 0)
	{
		printf( " failed\n  ! mbedtls_ctr_drbg_seed returned %d\n", ret );
		fflush( stdout );
		goto exit;
	}

	/*
	* Start the connection
	*/
	printf( "\n  . Connecting to tcp/%s/%s...", SERVER_NAME, SERVER_PORT );
	fflush( stdout );

	/*
	* Connect with mbedtls
	*/
	if( ( ret = mbedtls_net_connect( &server_fd, SERVER_NAME,
		                             SERVER_PORT, MBEDTLS_NET_PROTO_TCP ) ) != 0 )
	{
		printf( " failed\n  ! net_connect returned %d\n\n", ret );
		fflush( stdout );
		goto exit;
	}

	/*
	* Initialize the SSL context
	*/
	mbedtls_ssl_init( &ssl );
	mbedtls_ssl_config_init( &conf );
	printf( " ok\n" );

	printf("  . Setting up the SSL/TLS structure...");
	fflush( stdout );

    if( ( ret = mbedtls_ssl_config_defaults( &conf,
                                             MBEDTLS_SSL_IS_CLIENT,
                                             MBEDTLS_SSL_TRANSPORT_STREAM,
                                             MBEDTLS_SSL_PRESET_DEFAULT ) ) != 0 )
	{
		printf( " failed\n  ! mbedtls_ssl_config_defaults returned %d\n\n", ret );
		fflush( stdout );
		goto exit;
	}

	mbedtls_ssl_conf_authmode( &conf, MBEDTLS_SSL_VERIFY_NONE );

	mbedtls_ssl_conf_rng( &conf, mbedtls_ctr_drbg_random, &ctr_drbg );
	mbedtls_ssl_conf_dbg( &conf, my_debug, stdout );
	mbedtls_ssl_set_bio( &ssl, &server_fd, mbedtls_net_send, mbedtls_net_recv, NULL );

	if( ( ret = mbedtls_ssl_setup( &ssl, &conf ) ) != 0 )
	{
		printf( " failed\n  ! mbedtls_ssl_setup returned %d\n\n", ret );
		fflush( stdout );
		goto exit;
	}
	printf( " ok\n" );

	/*
	* Write the GET request
	*/
	printf( "  > Write to server:" );
	fflush(stdout);

	len = snprintf((char *)buf, sizeof(buf), GET_REQUEST);

	while( ( ret = mbedtls_ssl_write(&ssl, buf, len ) ) <= 0 )
	{
		if( ret != 0 )
		{
			printf( " failed\n  ! write returned %d\n\n", ret );
			fflush( stdout );
			goto exit;
		}
	}

	len = ret;
	printf( " %d bytes written\n\n%s", len, ( char * )buf );

	/*
	* Read the HTTP response
	*/
	printf( "  < Read from server:" );
	fflush( stdout );
	do
	{
		len = sizeof( buf ) - 1;
		memset( buf, 0, sizeof( buf ) );
		ret = mbedtls_ssl_read( &ssl, buf, len );
		if( ret == MBEDTLS_ERR_SSL_WANT_READ || ret == MBEDTLS_ERR_SSL_WANT_WRITE )
			continue;

		if( ret == MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY )
			break;

		if( ret < 0 )
		{
			printf( "failed\n  ! mbedtls_ssl_read returned %d\n\n", ret );
			fflush( stdout );
			break;
		}

		if( ret == 0 )
		{
			printf( "\n\nEOF\n\n" );
			fflush( stdout );
			break;
		}

		len = ret;
		printf(" %d bytes read\n\n%s", len, ( char *)buf );
	} while( 1 );
	mbedtls_ssl_close_notify( &ssl );

exit:

	mbedtls_net_free( &server_fd );
	mbedtls_ssl_free( &ssl );
	mbedtls_ssl_config_free( &conf );
	mbedtls_ctr_drbg_free( &ctr_drbg );
	mbedtls_entropy_free( &entropy );
	memset( &ssl, 0, sizeof( ssl ) );

#ifdef _WIN32
	printf( "  + Press Enter to exit this program.\n" );
	fflush( stdout ); getchar();
#endif

	return( ret );
}
```

Before compiling, you need to tell Visual Studio where to find the Mbed TLS files. In the solution explorer, right click on the project named **Mbed\_client\_demo**, and select **Properties**.

Under **Linker / Input / Additional Dependencies**, add: `mbedTLS.lib`. You can remove the wsock32.lib entry.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-17.png)</span>

Under **Linker / General / Additional Library Directories**, add : `..\\..\mbedtls-<version\>\visualc\VS2010\Release`. Write the version number with the one you installed. If you unpacked and compiled Mbed TLS in a different location, you can enter the full path to the location of the `mbedTLS.lib` file.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-18.png)</span>

Under **C/C++ / General / Additional Include Directories**, add: `..\\..\mbedtls-<version\>\include`. Use the same renaming as for the library directory mentioned above.

Click **OK**.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-19.png)</span>

### Compile and test

You can now build the modified sample application. Press **ctrl+shift+b**. Visual Studio shows `Build: 1 succeeded` in the output screen.

Start the application by pressing the **F5** key. The application shows a command screen stating that a connection has been made to the server and shows the server's response. This time, you are communicating over a secure TLS connection.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-20.png)</span>

## Use `cmake` to generate a Visual Studio solution file

You can use `cmake` to generate Visual Studio.

In a command prompt, change directory to the root folder of your Mbed TLS folder.

Type: `cmake -G "Visual Studio 14 2015 Win64"`

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-21.png)</span>

You have now generated a solution file in the root of your Mbed TLS folder.

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/MbedTLS-Tutorial-VS2015-22.png)</span>

You can now continue as described previously for the supplied Visual Studio solution file.

Note that the generated solution file created the library for `Win64` architecture(`x64`) (or `ARM`, depending on the parameters). You can also build the supplied solution file for Win32. When you write your sample application, build it with the same architecture that the library was built for.

## Further notes

This sample is for example use only. It doesn't authenticate the server with a trusted root certificate. In a larger project, you may want to wrap the code to call Mbed TLS in functions like: `InitializeSSL`, `OpenSSLConnection`, `ExecuteSSLRequest`, `ReadSSLResponse` and `CloseSSL`. You could also use a C++ class with which you can place the initialize and close functions in the constructor and destructor.

To ease the rollout of your application, you can copy the `mbedTLS.lib` files to the Debug and Release folders of your project.

<!-- using-mbedtls-in-microsoft-visual-studio-2015,"Walkthrough for compiling Mbed TLS with Visual Studio 2015","Visual Studio 2010, Visual Studio, MSVS2015","Microsoft, visual studio, msvc, windows, tutorial, snippet, VS2015, explanation,",published,"2012-10-09 00:00:00",6,12129,"2015-07-24 11:36:00","Paul Bakker" -->
