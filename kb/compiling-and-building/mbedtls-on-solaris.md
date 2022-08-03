# Mbed TLS on Solaris

When compiling Mbed TLS on Solaris, you might encounter some known issues. The default `Makefile` tries to manage as many systems as possible, but you must do some changes manually.

## Linking error

If you run `make`, you may get an error during linking similar to:

```
$ make
...
  CC    pkey/dh_client.c
Undefined                       first referenced
 symbol                             in file
bind                                ../library/libmbedtls.a(net.o)
accept                              ../library/libmbedtls.a(net.o)
listen                              ../library/libmbedtls.a(net.o)
gethostbyname                       ../library/libmbedtls.a(net.o)
socket                              ../library/libmbedtls.a(net.o)
setsockopt                          ../library/libmbedtls.a(net.o)
connect                             ../library/libmbedtls.a(net.o)
shutdown                            ../library/libmbedtls.a(net.o)
ld: fatal: symbol referencing errors. No output written to pkey/dh_client
collect2: ld returned 1 exit status
make[1]: *** [pkey/dh_client] Error 1
make: *** [all] Error 2
```

This is because under Solaris, you must to instruct GCC to include `libsocket` and `libnsl` during linking.

Define `LDFLAGS` to include `-lsocket -lnsl` when running `make` on Solaris 10.

## Ar error

If you run `make` and receive the following error:

```
$ make
....
  AR    libmbedtls.a
ar: creating libmbedtls.a
  RL    libmbedtls.a
ar: one of [drqtpmx] must be specified
make[1]: *** [libmbedtls.a] Error 1
make: *** [all] Error 2
```

### Workaround

Install the package `SUNWbinutils`, then run:

```
export AR=gar
```


<!--- mbedtls-on-solaris,"When compiling Mbed TLS on Solaris some modifications might be needed in the Makefile or a package must be installed","Solaris, Makefile, undefined symbol, linking, bind, accept, listen, socket, connect, ar, make, gar","Solaris, build, compile,, Makefile, undefined symbol, linking, bind, accept, listen, socket, connect, ar, make, gar, setsockopt, gethostbyname, shutdown, libsocket, libnsl, ldflags",published,"2013-06-27 11:43:00",6,3122,"2015-07-24 11:39:00","Paul Bakker" --->
