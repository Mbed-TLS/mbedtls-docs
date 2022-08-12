# How to generate a Certificate Request (CSR)

This tutorial describes how to generate your own certificate request for use in an online SSL certificate request.

Mbed TLS includes the core and applications for generating keys and certificate requests without relying on other libraries and applications, offering users a command-line alternative to OpenSSL for generating their keys and certificate requests.

This article assumes you have compiled and installed the Mbed TLS library and example programs on your system.

## Certificate Request for use with SSL vendors

Whenever you request a certificate from one of the SSL vendors, you are asked to enter a CSR. CSR is short for Certificate Signing Request and is often in the PEM format.

To generate a certificate request, you need a private-public key pair. The public key is put in the certificate request in addition to some identifying information (such as website domain, address, and country). By submitting your request, you ask the SSL vendor to sign that request with their CA key and generate a full certificate from it.

The CA will determine the validity of the certificate they generate based on how much you paid them.

## Generating a RSA key file

The first step for generating a certificate request, is to generate a private-public key pair for the certificate.

For generating key files, Mbed TLS includes the `gen_key` application in `programs/pkey`.

This key generation application accepts the following arguments:
```
 usage: gen_key param=<>...

 acceptable parameters:
    type=rsa              default: rsa
    rsa_keysize=%d        default: 4096
    filename=%s           default: keyfile.key
    format=pem|der        default: pem
```
The following command generates a 2048 bit RSA key file, as explained [here](/kb/cryptography/rsa-key-pair-generator.md):
```
programs/pkey/gen_key type=rsa rsa_keysize=2048 filename=example.com.key
```

## Generating certificate request

For generating and writing certificate files, Mbed TLS includes the `cert_req` application in `programs/x509`.

Before generating the certificate request you need to determine the different values that need to go in it.

### Key to use in the certificate

First and foremost a certificate binds a public-private key pair to an identity. To indicate which key to use in the certificate request you use the `filename` argument, like so `filename=example.com.key`.

### Subject name

Each certificate request needs a subject name (the identity that is being signed). Each CA vendor has different requirements for which items are required in a certificate request.

If you want to request a certificate for the `example.com` domain name from the organization `Example Ltd` in the country `UK`, you should use `subject_name=CN=example.com,O=Example\ Ltd,C=UK` on the command-line.

<span class="notes">**Note:** If you want to use a space in one of the names you have to either nullify it (`issuer_name=CN=my\ server`) or contain the entire argument in quotation marks (`"issuer_name=CN=my server"`).</span>

<span class="notes">**Note:** Commas inside names need to be nullified with a backslash as well. You need to protect the backslash from your shell, for example, `issuer_name=CN=my\\\,server` or `issuer_name='CN=my\,server'`.</span>

The available items you can put in a `subject_name` (that you support) are:

* C = Country
* CN = Common Name
* L = Locality
* O = Organization
* OU = Organizational Unit
* R = e-mail address
* ST = State
* serialNumber
* postalAddress
* postalCode

### Command to generate a certificate request

So the full command for generating a certificate request for `example.com.key` with the name `CN=example.com,O=Example Ltd,C=UK` would be:
```
programs/x509/cert_req filename=example.com.key                          \
                       subject_name=CN=example.com,O=Example\ Ltd,C=UK \
                       output_file=example.com.req
```
The file `example.com.req` now contains your PEM-encoded certificate request. It will look something like:
```
-----BEGIN CERTIFICATE REQUEST-----
MIICgTCCAWkCAQAwPDEVMBMGA1UEAxMMcG9sYXJzc2wub3JnMRYwFAYDVQQKEw1P
ZmZzcGFyayBCLlYuMQswCQYDVQQGEwJOTDCCASIwDQYJKoZIhvcNAQEBBQADggEP
ADCCAQoCggEBAJ8NFeCvO7F1DJhkZEUZpt8x9x7BBxW9odeORDcNFSifNyh1ywRi
HMMWbR6JwQDiCqBMLZ9kOktv3VXpTSAD15vwYGPQHnD9Cs3kHc7DDaj27KerSFgH
oYE4/MxAadeXGIYMjmFqCbJ6Y+3CDxWn5V9TkFkXOJHZb3EKjOEPq5Zjrvdr1vPC
/C1+GUFAkIIo2y044uZTH3oFcSXx0xCK5yjZEfa+x1PzYaugAInVcj+43VLTOJWP
4RaHgUnNwE/D1HgX8DKKRvDE2uJY6sU+EXd2J9GhijqarvCcVNfYWzX+bsicjl4k
K4u7TVWN95c4KtJ+spq+YPP+PkUyTqvrkgECAwEAAaAAMA0GCSqGSIb3DQEBBQUA
A4IBAQAOmMR3z53yz7haJbpl2GNTwDBs8UKzGexJ+OBC+Jww2NEbXeN0HSQdQhMD
R7GJVO7CslWELcwn9TDCZjNDTSL95YNputzA0yhfu3/9HTeWGwR1X3oH+FjVCPD2
JkUn1A/l4FnCgxraC2YoaKxnpGj3qe2dq4y9j/rB5yrOjyqfvHhSmm83ktWHqsa/
TuOXC/24Dsc4iHapiWo+F5WO2jWOj+HE22y7i9O/dcth6Gv37tUFhqB8X++TfNkj
62O45O/iBEGNebBD/r90a+Z+FOa5k3FgJ34hTqts3UhD8UPgQ0q8x8aSbGOjykrD
+F2IMb01ggOxT9qOBlRLHRhVDkqV
-----END CERTIFICATE REQUEST-----
```
You can copy and paste the PEM content into the website for the certificate vendor.

<!---",generate-a-certificate-request-csr,"Step-by-step guide on how to generate a certificate request with Mbed TLS instead of OpenSSL for use with an online SSL certificate vendor",,"generate, certificate request generation, cert_req, gen_key, CA certificate",published,"2014-02-11 12:18:00",2,15507,"2015-07-02 11:28:00","Paul Bakker"--->
