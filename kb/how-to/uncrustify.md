# Using uncrustify in Mbed TLS

## Installing uncrustify

Note that you need uncrustify 0.75.1. Older or newer versions produce different output. This section contains some tips on installing the required version of uncrustify.

### Compiling from source

You need a C++ compiler, CMake, and Python 3. The following instructions work on most systems with development tools installed:

```sh
git clone https://github.com/uncrustify/uncrustify
git checkout uncrustify-0.75.1
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
```
This creates an `uncrustify` executable in the `build` directory. Copy it somewhere on your command search `PATH`. Optionally, also install the manual page `uncrustify.1`.

### macOS: installing an older uncrustify from Homebrew

```sh
brew tap-new local/for-mbedtls
brew extract --version=0.75.1 uncrustify local/for-mbedtls
brew install local/for-mbedtls/uncrustify@0.75.1
```

If you also have the latest uncrustify installed, the `install` command will complain that it can’t create the `uncrustify` symbolic link, but you still have uncrustify 0.75.1 available at `/opt/homebrew/Cellar/uncrustify@0.75.1/0.75.1/bin/uncrustify` (if the brew prefix is `/opt/homebrew`). Put `/opt/homebrew/Cellar/uncrustify@0.75.1/0.75.1/bin` first in your `PATH` when working on Mbed TLS.

### Windows binaries

You can download [official Windows binaries hosted on Sourceforge](https://sourceforge.net/projects/uncrustify/files/).
