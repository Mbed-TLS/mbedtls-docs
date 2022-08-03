# Adding support for additional subject alternative names

[RFC 5280 section 4.2.1.6](https://tools.ietf.org/html/rfc5280#section-4.2.1.6) defines the following as options for a subject alternative name (SAN):

    SubjectAltName ::= GeneralNames

    GeneralNames ::= SEQUENCE SIZE (1..MAX) OF GeneralName

    GeneralName ::= CHOICE {
         otherName                       [0]     OtherName,
         rfc822Name                      [1]     IA5String,
         dNSName                         [2]     IA5String,
         x400Address                     [3]     ORAddress,
         directoryName                   [4]     Name,
         ediPartyName                    [5]     EDIPartyName,
         uniformResourceIdentifier       [6]     IA5String,
         iPAddress                       [7]     OCTET STRING,
         registeredID                    [8]     OBJECT IDENTIFIER }

    OtherName ::= SEQUENCE {
         type-id    OBJECT IDENTIFIER,
         value      [0] EXPLICIT ANY DEFINED BY type-id }

    EDIPartyName ::= SEQUENCE {
         nameAssigner[0] DirectoryString OPTIONAL,
         partyName   [1] DirectoryString }

Mbed TLS does not support parsing and writing all of these SAN types, at the moment; however, the certificate structure contains the full raw data for all subject alternative names, in its `subject_alt_names` variable.

This document provides guidelines for adding parsing support for additional SAN types.

The following definitions correspond to the name types defined in the RFC:

    #define MBEDTLS_X509_SAN_OTHER_NAME                      0
    #define MBEDTLS_X509_SAN_RFC822_NAME                     1
    #define MBEDTLS_X509_SAN_DNS_NAME                        2
    #define MBEDTLS_X509_SAN_X400_ADDRESS_NAME               3
    #define MBEDTLS_X509_SAN_DIRECTORY_NAME                  4
    #define MBEDTLS_X509_SAN_EDI_PARTY_NAME                  5
    #define MBEDTLS_X509_SAN_UNIFORM_RESOURCE_IDENTIFIER     6
    #define MBEDTLS_X509_SAN_IP_ADDRESS                      7
    #define MBEDTLS_X509_SAN_REGISTERED_ID                   8

**To add parsing support for an additional SAN:**

1. In the `X509_crt.h` file, update the following struct to support your new SAN type:

    ```
    typedef struct mbedtls_x509_subject_alternative_name
    {
        int type;                              /**< The SAN type, value of MBEDTLS_X509_SAN_XXX. */
        union {
            mbedtls_x509_san_other_name other_name; /**< The otherName supported type. */
            mbedtls_x509_buf   unstructured_name;   /**< The buffer for the un constructed types. Only dnsName is currently supported. */
        }
        san; /**< A union of the supported SAN types */
    }
    mbedtls_x509_subject_alternative_name;  
    ```

    - An `unstructured_name` is any SAN type that has only an ASN.1 tag, and data, such as `OCTET STRING` and `IA5String`. To add `ediPartyName` or `x400Address`, add the relevant structure to the `san` union.

    - You define the `otherName` type explicitly by setting its `type-id`.

    To add a new `otherName` type, modify the `value` union in the following struct, and add a relevant comment with a reference to the RFC that defines the new type:

    ```
      typedef struct mbedtls_x509_san_other_name
      {
        /**
         * The type_id is an OID as defined in RFC 5280.
         * To check the value of the type id, you should use
         * \p MBEDTLS_OID_CMP with a known OID mbedtls_x509_buf.
         */
        mbedtls_x509_buf type_id;                   /**< The type id. */
        union
        {
            /**
             * From RFC 4108 section 5:
             * HardwareModuleName ::= SEQUENCE {
             *                         hwType OBJECT IDENTIFIER,
             *                         hwSerialNum OCTET STRING }
             */
            struct
            {
                mbedtls_x509_buf oid;               /**< The object identifier. */
                mbedtls_x509_buf val;               /**< The named value. */
            }
            hardware_module_name;
        }
        value;
    }
    mbedtls_x509_san_other_name;
    ```

    <span class="notes">**Note:** You must also add the OID of the `type-id` to the `oid.h` file.</span>

1. Modify the `mbedtls_x509_parse_subject_alt_name()` function to support your new type.

    For example, add `iPAddress`:

    ```
    /*
     * iPAddress
     */
    case( MBEDTLS_ASN1_CONTEXT_SPECIFIC | MBEDTLS_X509_SAN_IP_ADDRESS ):
    {
        memset( san, 0, sizeof( mbedtls_x509_subject_alternative_name ) );
        san->type = MBEDTLS_X509_SAN_IP_ADDRESS;

        memcpy( &san->san.unstructured_name,
                san_buf, sizeof( *san_buf ) );

    }
    break;
    ```

    This copies the raw data of the SAN certificate to your `mbedtls_x509_subject_alternative_name` struct.

    For a new `otherName` type, you must modify the `x509_get_other_name()` function with your specific use case.

1. Modify the `x509_info_subject_alt_name()` function to support your new type.

    For example, add `iPAddress`:

    ```
    /*
     * iPAddress
     */
    case MBEDTLS_X509_SAN_IP_ADDRESS:
    {
        ret = mbedtls_snprintf( p, n, "\n%s    ipAddress : ", prefix );
        MBEDTLS_X509_SAFE_SNPRINTF;
        if( san.san.unstructured_name.len >= n )
        {
            *p = '\0';
            return( MBEDTLS_ERR_X509_BUFFER_TOO_SMALL );
        }

        memcpy( p, san.san.unstructured_name.p, san.san.unstructured_name.len );
        p += san.san.unstructured_name.len;
        n -= san.san.unstructured_name.len;
    }
    break;
    ```

1. Modify `x509_crt_verify_name()`, if needed.

1. Add tests for your new SAN type to the `test_suite_x509parse.data` file, including:

    - The `x509_cert_info` test, running various certificate parsing scenarios using the relevant SAN type.

    - The `x509parse_crt` test, running negative parsing scenarios with invalid data.
