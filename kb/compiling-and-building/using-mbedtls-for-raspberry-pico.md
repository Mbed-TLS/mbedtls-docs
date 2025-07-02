# Arm Mbed TLS in Raspberry Pi Pico SDK

## Introduction

This tutorial shows how to use the Mbed TLS cryptography library from the pico sdk (source at https://github.com/raspberrypi/pico-sdk) in projects. As of writing this only Mbed TLS 2.28 is supported with the SDK. This project will ultimately end up with setting up programs/hash/hello.c from the mbedtls repository on your own Pico board.

## Setting up the SDK

First, you will need to clone the sdk in your prefered place with 
```
git clone https://github.com/raspberrypi/pico-sdk
``` 
Next we need to initialise and update the submodules. If you are developing for the Pico W you need to run

```
git submodule add https://github.com/georgerobotics/cyw43-driver
```

Then set all the submodules up with

```
git submodule update --init
```
Mbed TLS 2.28 will now be ready to use from the sdk

## Setting up the project for PICO board

Then outside of the sdk, make a directory where you would like to do development. You can find the example we are trying to build at `<path-to-sdk>/lib/mbedtls/programs/hash/hello.c` and copy it into the development directory. Some changes need to be made to this file to make it compatible for the pico board. Add the line `stdio_init_all();` at the top of the main loop to set up the I/O functionality. Also to be able to see the output once the board is running you might want to surround the body of the program in a while true loop.

Now you'll need to copy the cmake file which finds the sdk from your project:
```
cp <path-to-sdk>/external/pico_sdk_import.cmake .
```
Then make a `CMakeLists.txt` file with the following
```
cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(hello C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(hello
    hello.c
)

pico_enable_stdio_usb(hello 1)
pico_enable_stdio_uart(hello 1)
pico_add_extra_outputs(hello)

target_link_libraries(test pico_stdlib pico_mbedtls)
target_include_directories(test PRIVATE ${CMAKE_CURRENT_LIST_DIR} )
```
When including `pico_mbedtls`, a config file is automatically searched for with the name `mbedtls_config.h` so make a new file for new with the line
```
#define MBEDTLS_MD5_C
```
so we can run the main loop in our program. Then make a build a directory and run
```
cmake .. && make
```
This will generate a .uf2 file that you can use on your pico board. To put the firmware on your pico baord, hold down the BOOTSEL button on the board, and then connect it to your device. Hold it down until the board mounts as mass storage device. Once it's mounted you can copy the uf2 file onto the board, at which point the board will reboot and start running the firmware. We enabled USB I/O in makefile, so we need to connect to the serial port the pico's usb is connected to.

### Linux systems

On linux by default this will be visible at `/dev/ttyACM0`. To connect and see the output to ensure your board is running, run:
```
minicom -b 115200 -o -D /dev/ttyACM0
```
And you should be able to see your program running.

### Other systems

You can use any serial monitor, such as putty, and connect to the port you find your raspberry board connected to with a baud rate of 115200.

## Extra considerations for the PICO W

Although this example doesn't utilise it, you may want to use some Pico W functionality, for many other projects. In this case, you will need to also target a cyw43 library in the cmake file. For more information on this, see [here](https://www.raspberrypi.com/documentation/pico-sdk/networking.html).

<!--- "This quickstart manual is intended for C/C++ developers who are interesting in developing Mbed TLS based projects in Eclipse C/C++ Development Tool (CDT) on Windows.","Eclipse CDT, Cygwin, Eclipse installation","eclipse, cygwin, tutorial",published,"2013-01-04 15:39:00",6,47375,"2015-07-24 11:51:00","Paul Bakker"--->