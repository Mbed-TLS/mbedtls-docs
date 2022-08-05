# How to generate a self-signed certificate

This tutorial outlines how to generate your own keys and certificates for your system.

Mbed TLS includes the core and applications for generating keys and certificates without relying on other libraries and applications, giving you a command-line alternative to OpenSSL for generating their keys and (self-signed) certificates.

This article assumes you have compiled and installed the Mbed TLS library on your system.

## Generating a RSA key file

The first step for generating a self-signed certificate is to generate a private/public key pair for the certificate.

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
The following command generates a 4096 bit RSA key file, as explained [here](https://tls.mbed.org/kb/cryptography/rsa-key-pair-generator):
```
programs/pkey/gen_key type=rsa rsa_keysize=4096 filename=our_key.key
```

## Generating a self-signed certificate

For generating and writing certificate files, Mbed TLS includes the `cert_write` application (located in `programs/x509`).

Before generating the self-signed certificate, determine the different values in it.

In the case of a self-signed certificate, indicate it with `selfsign=1`.

### Key to use in the certificate

First and foremost a certificate binds a public-private key pair to an identity. To indicate which key to use to sign the certificate we use the `issuer_key` argument, like so `issuer_key=our_key.key`.

Because this is a self-signed certificate the `subject_key` is automatically identical.

### Subject name / Issuer name

Each certificate is identified with a subject name (the identity that is being signed) and an issuer name (the party doing the signing). For self-signed certificates, only the issuer name is used.

In case we want to name the issuer `myserver` from the organization `myorganization` and the country `NL`, we should use `issuer_name=CN=myserver,O=myorganization,C=NL` on the command-line.

<span class="notes">**Note:** If you want to use a space in one of the names you have to either nullify it (`issuer_name=CN=my\ server`) or contain the entire argument in quotes (`"issuer_name=CN=my server"`).</span>

<span class="notes">**Note:** Commas inside names need to be nullified with a backslash as well. You need to protect the backslash from your shell, for example, `issuer_name=CN=my\\\,server` or `issuer_name='CN=my\,server'`.</span>

The supported items in a `subject_name` are:

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

## Validity

Each certificate contains within it the validity period for that certificate indicated by the **not_before** and **not_after** values.

The applications accepts values of the format **YYYYMMDDHHMMSS**, so to indicate that a certificate is not valid before 2013, you can use `not_before=20130101000000` and not valid after 2015, you can use `not_after=20151231235959`.

## Is it a CA certificate?

If you want this self-signed certificate to be a CA certificate capable of signing other certificates, enable it with `is_ca=1`.

You then need to decide if this CA certificate can only sign regular certificates (`max_pathlen=0`) or if it is at the top of other intermediate CA certificates.

## Command to generate a self-signed certificate

**Example:**

The full command for generating a self-signed CA certificate that cannot sign other CA certificates for `our_key.key` with the name `CN=myserver,O=myorganization,C=NL` and valid only in the years 2013, 2014 and 2015 would be:
```
programs/x509/cert_write selfsign=1 issuer_key=our_key.key                    \
                         issuer_name=CN=myserver,O=myorganization,C=NL        \
                         not_before=20130101000000 not_after=20151231235959   \
                         is_ca=1 max_pathlen=0 output_file=my_crt.crt
```
The file `my_crt.crt` now contains your PEM-encoded certificate.

### Key usage and NS cert type extension

You can set the key usage extension and the NS Cert type extension in the certificate on the command-line as well with:
```
    key_usage=%s        default: (empty)
                        Comma-separated-list of values:
                          digital_signature
                          non_repudiation
                          key_encipherment
                          data_encipherment
                          key_agreement
                          key_certificate_sign
                          crl_sign
    ns_cert_type=%s     default: (empty)
                        Comma-separated-list of values:
                          ssl_client
                          ssl_server
                          email
                          object_signing
                          ssl_ca
                          email_ca
                          object_signing_ca
```
<!---generate-a-self-signed-certificate
,"Step-by-step guide on how to generate a self-signed certificate with Mbed TLS instead of OpenSSL.",,"generate, certificate generation, self-signed, cert_write, gen_key, CA certificate",published,"2013-10-31 12:13:00",2,19910,"2015-07-02 11:48:00","Paul Bakker"--->
