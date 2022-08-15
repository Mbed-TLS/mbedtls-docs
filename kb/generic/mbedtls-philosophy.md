# Mbed TLS design

## The philosophy behind Mbed TLS

Mbed TLS takes a lean-and-mean approach to software development. We have designed it to be easy to use by being readable, documented, tested, loosely coupled and portable.


### Documented

Mbed TLS has a large amount of documentation online, including the [full doxygen API documentation](/api), the [Design Documentation for security evaluations](/high-level-design), [example applications](/source-code) and more.


### Tested

The automatic test suites contain over 6000 unit tests for cryptographic validation, regression testing and code coverage, over 200 functional tests and over 2000 interoperability tests. See our [quality assurance page](what-tests-and-checks-are-run-for-polarssl.md) for more details.


### Loosely coupled

The Mbed TLS modules are as loosely coupled as possible. If you want to use AES, then copy `aes.c` and `aes.h`. No other files are required and this is valid for all symmetric and hash algorithms. Other modules are as straightforward, though some require the modules that they are dependent on. All portability code is present in the modules themselves. While, in some cases, this can create duplicate defines, putting the portability code in a central header-file allows for the loose coupling that we are aiming for.


### Portable

Mbed TLS is written in portable C code. As mentioned in the [coding standards article](../development/mbedtls-coding-standards.md#iso-c99), the library uses the C99 ISO standard.


<!--'mbedtls-philosophy','Mbed TLS is designed according to a specific philosophy','PolarSSL, philosophy, loose-coupling, easy','philosophy, loose-coupling, easy, tests, portable','published','2012-10-07 00:00:00','1','3606','2015-07-24 11:49:00','Paul Bakker'-->
