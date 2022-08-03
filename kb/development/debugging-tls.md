# Debugging TLS sessions

It is important to understand why a TLS handshake has failed with Mbed TLS and this short article will guide you through ways to debug Mbed TLS within your application. Using a debugger is an important first step, but will not always assist in understanding the cause of failure for a long complex TLS handshake. If using a debugger does not help explain the issue, then we recommend the following steps to reproduce and debug the failure.

## Enable logs in Mbed TLS

Mbed TLS has a feature to show the TLS handshake logs, filtering with certain debug level. In order to see the TLS logs in your terminal, you must verify that you have `MBEDTLS_DEBUG_C` defined in your configuration.

Set the debug threshold for the TLS handshake:
```
mbedtls_debug_set_threshold( <debug_level> )
```  
Note that `debug_level` is the level of debug logs you require. Its values can be between 0 and 5, where 5 is the most logs.  
Set your debug log function to display in your terminal:
```
mbedtls_ssl_conf_dbg()
```
These steps will enable logs and print the logs according to your debug function.

## Use Sample applications

Mbed TLS comes with a variety of sample applications that run on your desktop machine in the `programs` folder. We recommended that you first try using one of these sample applications in the `ssl` programs sub-folder to eliminate issues unrelated to your platform, such as certificate handling and configuration setup. Most of the ssl sample applications have a `debug_level` application parameter to show TLS logs.  
You should use the sample application to eliminate issues related to the peer, and use a known server \ client for your porting process.  
For example, if you are porting a TLS client and have issues connecting to a server, then you should run the following setups with debug logs enabled:

1. Run `ssl_client2` and `ssl_server2` to first understand the basic TLS connection.
1. Run `ssl_client2` with the server you are trying to connect to. This will help you understand what CA root certificate you need to set in `mbedtls_ssl_conf_ca_chain()`.
1. Run `ssl_server2` with your client application. This will have you working with a known server, and help you test your specific porting setup.
1. Run your client application with the server you are trying to connect to. Once the previous steps have been completed, you should test the final setup, to get past all the TLS related issues.

If you still encounter problems after trying these steps, then it is likely that your issue is platform specific, such as a memory related issue.
