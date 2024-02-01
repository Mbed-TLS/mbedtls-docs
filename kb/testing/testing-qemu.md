# Testing non-native architectures with QEMU

This page shows how to test Mbed TLS on Linux for CPUs you don't have, assuming the target CPU can also run Linux.

## Preparing Ubuntu for building and testing with QEMU

Add other targets to your package sources in a new file `/etc/apt/sources.list.d/ubuntu-foreign.list`. Note that ordinary Ubuntu mirrors only have PC builds, so you need a `ports` mirror. For example:

```
deb [arch=arm64,armhf,ppc64,s390x] http://fr.ports.ubuntu.com/ubuntu-ports focal main restricted universe multiverse
deb [arch=arm64,armhf,ppc64,s390x] http://fr.ports.ubuntu.com/ubuntu-ports focal-security main restricted universe multiverse
deb [arch=arm64,armhf,ppc64,s390x] http://fr.ports.ubuntu.com/ubuntu-ports focal-updates main restricted universe multiverse
```

Then install `libc6-dev` for the desired architectures.

```
sudo apt-get update
sudo apt-get install libc6-dev:arm64 libc6-dev:armhf libc6-dev:ppc64 libc6-dev:s390x
```

## Testing with qemu-user on Linux

### Cmake build

For example for aarch64:

```
mkdir build-aarch64
cd build-aarch64
CC=clang CFLAGS="--target=aarch64-linux-gnu" cmake -DCMAKE_BUILD_TYPE=Release ..
make -j2
cd tests
qemu-aarch64 -L /usr/aarch64-linux-gnu ./test_suite_mpi
```

### mtest

With [mtest](https://github.com/Mbed-TLS/mbedtls-docs/blob/main/tools/bin/mtest):

```
mtest <arch> <test names>
```

e.g.

```
mtest aarch64 cmac
```

### mbedtls-prepare-build

With [mbedtls-prepare-build](https://github.com/ARMmbed/mbedtls-docs/blob/main/tools/bin/mbedtls-prepare-build):

```
mbedtls-prepare-build -d build-aarch64 --cc=clang --cflags='-O2 -target aarch64-linux-gnu' --qemu-ld-prefix=aarch64-linux-gnu
make -C build-aarch64 test
```

