# Compile cURL with Arm Mbed TLS

This tutorial shows you how to compile the popular cURL library with Mbed TLS as the cryptography library. This step-by-step tutorial uses Ubuntu as the operating system. This tutorial does everything from a shell. We tested this example with versions mbedtls-2.12.0 and curl-7.61.0

## Download Mbed TLS

The Mbed TLS library is not included in the cURL source package, so you need to download and install Mbed TLS first. You can use the latest version by altering the version number in the URL below. Enter these statements to download and unpack the Mbed TLS source code to your `/home/Downloads` folder:

```
cd ~/Downloads
wget https://tls.mbed.org/code/releases/mbedtls-2.12.0-gpl.tgz
tar -zxf mbedtls-2.12.0-gpl.tgz
cd mbedtls-2.12.0
```

## Compile and install Mbed TLS

Now compile the source code by entering:

```
make CFLAGS=-fPIC
```

Optionally, you can check that Mbed TLS works correctly by entering:

```
make check
```

To install the library, enter:

```
sudo make install
```

Note that you need administrator privileges to execute this command. The Mbed TLS library is now installed in `/usr/local/lib`.

## Download cURL

To download and unpack the cURL source code, enter these statements (You can use the latest version by altering the version number in the URL):

```
cd ~/Downloads
wget http://curl.haxx.se/download/curl-7.61.0.tar.gz
tar -zxf curl-7.61.0.tar.gz
cd curl-7.61.0
```

## Compile and install cURL

To compile cURL with Mbed TLS, you need to configure the build system. Normally you would use the configure script without any options, but in this case some options are needed. Enter:

```
./configure --without-ssl --with-mbedtls
```

The `without-ssl` and `with-mbedtls` parameters instruct the build system to use Mbed TLS instead of the default SSL library. When the configure script finishes, it states something like this:

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/mbedtls-tutorial-curl-1.png)<span>Compile and install cURL</span></span>

To compile and install cURL, enter:

```
make
sudo make install
```

You need administrator privileges to execute the second command. The cURL program is now installed in `/usr/local/bin`.

## Test cURL

To test the installation, you can enter:

```
curl -V
```

This confirms that cURL is using Mbed TLS. To test the SSL capabilities of cURL, you can retrieve an HTML header with an HTTPS request:

```
curl -I https://www.google.com/
```

The result is something like this:

<span class="images">![](https://mbed-tls-docs-images.s3.amazonaws.com/mbedtls-tutorial-curl-2.png)<span>Test cURL</span></span>

<span class="notes">**Note:** If you see the `libcurl.so.4: cannot open shared object file: No such file or directory` error, you need to type `ldconfig` first.</span>

<span class="notes">**Note:** You may need to add the path to `libcurl.so` ( `/usr/local/lib`) to your `LD_LIBRARY_PATH`.</span>

## Cygwin

Some additional information for Cygwin users.

- First, uninstall the standard cURL package from your Cygwin installation if it is installed. You can use the command `cygcheck -c` to print your installed packages.
- Before you can `wget` the Mbed TLS code, you need a bundle of X.509 certificates inside your Cygwin environment.

   ```
   pushd /usr/ssl/certs
   curl http://curl.haxx.se/ca/cacert.pem | awk 'split_after==1{n++;split_after=0} /-----END CERTIFICATE-----/ {split_after=1} {print >    "cert" n ".pem"}'
   
   c_rehash
   ```
   
- Create an extra symlink for wget

   ```
   ln -sT /usr/ssl /etc/ssl
   ```

- Configure the cURL build system with the following options:

   ```
   ./configure --without-ssl --with-mbedtls=/usr/local --with-ca-bundle=/etc/ssl/certs/ca-bundle.crt
   ```
   
The option `with-mbedtls` points to your Mbed TLS location and `with-ca-bundle` is the location of your certificates bundle you extracted before.

<!---compile-curl-with-mbedtls,
"A short tutorial on how to compile cURL with mbed TLS",
"cURL, compiling cURL, compile cURL, Mbed TLS",
"compiling cURL, cURL, tutorial, cygwin",published,
"2012-10-09 00:00:00",2,9275,
"2015-07-24 11:35:00",
"Paul Bakker"--->
