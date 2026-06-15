# MSVC on Linux

## Installation with msvc-wine

This section explains how to install MSVC on Linux via [msvc-wine](https://github.com/mstorsjo/msvc-wine).

### Prerequisites

Make sure that Wine and `msitools` are installed. For example, on Debian/Ubuntu:

```
apt-get install -y ca-certificates msitools wine64
```

You also [need `winbind` for debug builds](https://github.com/mstorsjo/msvc-wine#can-it-build-debug-versions).

### Installing the installer

```
git clone https://github.com/mstorsjo/msvc-wine
cd msvc-wine
```

### Installing Visual Studio 2017

See https://learn.microsoft.com/en-us/cpp/overview/compiler-versions?view=msvc-180 for how Visual Studio years match version numbers (and also corresponding `_MSC_VER` and MSVC built tools version).

```
./vsdownload.py --major 15 --dest ~/Packages/Visual_Studio_2017
./install.sh ~/Packages/Visual_Studio_2017
```

You will need to accept the license.

## Compiling TF-PSA-Crypto

### Getting started with CMake

```
CC=~/Packages/Visual_Studio_2017/bin/x64/cl PATH=$PATH:~/Packages/Visual_Studio_2017/bin/x64 cmake -GNinja -B build-default-msvc-release-ninja -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_POLICY_DEFAULT_CMP0141=NEW -DCMAKE_MSVC_DEBUG_INFORMATION_FORMAT=Embedded -DENABLE_TESTING=1 -DCMAKE_BUILD_TYPE=Release
ninja -C build-default-msvc-release-ninja test_suite_platform.exe
(cd build-default-msvc-release-ninja/tests && wine test_suite_platform.exe)
```

* `cl` (or `cl.exe`) is the compiler program from MSVC.
* You need `rc.exe` and maybe other tools that come with MSVC in the executable search path for the `cmake` step, but not when building.
* `-DCMAKE_POLICY_DEFAULT_CMP0141=NEW -DCMAKE_MSVC_DEBUG_INFORMATION_FORMAT=Embedded` are [necessary if you aren't running `winbind`](https://github.com/mstorsjo/msvc-wine#does-it-work-with-cmake). Note that you also need CMake &gt;=3.23.
* Remove `-GNinja` and replace `ninja` by `make` if you prefer to build with Make.

### Building the full config

We don't provide support for threads on Windows, so you need to disable `MBEDTLS_THREADING_C`, which the `full` config enables.

```
printf '%s\n' '#undef MBEDTLS_THREADING_C' '#undef MBEDTLS_THREADING_PTHREAD' >tests/configs/user-config-no-threading.h
CC=~/Packages/Visual_Studio_2017/bin/x64/cl PATH=$PATH:~/Packages/Visual_Studio_2017/bin/x64 cmake -GNinja -B build-full-msvc-release-ninja -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_POLICY_DEFAULT_CMP0141=NEW -DCMAKE_MSVC_DEBUG_INFORMATION_FORMAT=Embedded -DENABLE_TESTING=YES -DCMAKE_BUILD_TYPE=Release -DTF_PSA_CRYPTO_CONFIG_NAME=full -DTF_PSA_CRYPTO_USER_CONFIG_FILE=$PWD/tests/configs/user-config-no-threading.h
```

## Miscellaneous notes

### Harmless warnings

Ignore warnings like this one, it's expected in our code base.
```
aesce.c.obj : warning LNK4221: This object file does not define any previously undefined public symbols, so it will not be used by any link operation that consumes this library
```
