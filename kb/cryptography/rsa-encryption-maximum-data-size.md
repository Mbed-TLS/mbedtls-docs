# RSA encryption maximum data size

RSA is only able to encrypt data to a maximum amount equal to your key size (2048 bits = 256 bytes), minus any padding and header data (11 bytes for PKCS#1 v1.5 padding).

As a result, it is often not possible to encrypt files with RSA directly (and RSA is not designed for this). If you want to encrypt more data, you can do something like:

1. Generate a 256-bit random keystring K.
1. Encrypt your data with AES-CBC with K.
1. Encrypt K with RSA.
1. Send both to the other side.

Of course you can also use another key-size, symmetric algorithm and cipher mode - but you get the gist.
