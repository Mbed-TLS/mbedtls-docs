# Setting up a Python environment for Mbed TLS

## Python and package versions

Each branch of Mbed TLS has different minimum requirements on Python. See `README.md` in the branch. Any Python version that's more recent than the minimum should work, however as of November 2022 this is not well tested by the CI so unintended incompatibilities can happen.

Some of the scripts used by Mbed TLS users and developers require third-party packages. Those have version constraints as well. The constraints are documented via `*.requirements.txt` files in the [`scripts` directory](https://github.com/Mbed-TLS/mbedtls/tree/development/scripts).

We run [mypy](http://mypy-lang.org/) and [pylint](https://pylint.pycqa.org/en/latest/) to check Python scripts. It is common that newer versions of Pylint reject our code, because some checks have become stricter or new checks have been added.

## Set up a Python package environment

### What is a virtual environment?

A **[virtual environment](https://realpython.com/python-virtual-environments-a-primer/)** (**venv** for short) is a directory tree containing an autonomous set of Python packages. The venv is completely independent from the system installation, except for the Python executable itself and the standard library. System packages are not visible in the venv, so the venv can have its own version, and you can even test what happens when a package is missing by creating a venv without it.

### Creating a virtual environment for Mbed TLS

Summary:

```sh
python3 -m venv ~/venv-mbedtls-development
~/venv-mbedtls-development/bin/python scripts/min_requirements.py
```

To create a virtual environment, invoke the [`venv` module](https://docs.python.org/3/library/venv.html) (which ships with Python) with one argument, which is the path to the directory to create.

To set up a virtual environment with the reference setup used on the Mbed TLS CI, check out [mbedtls](https://github.com/Mbed-TLS/mbedtls) and run Mbed TLS's `scripts/min_requirements.py` explicitly with the desired venv's Python:
```sh
~/venv-mbedtls-development/bin/python scripts/min_requirements.py
```
Using the virtual environment's Python ensures that the packages are installed inside the virtual environment, and not system-wide or in your home directory.

You can also run `scripts/min_requirements.py` after [activating the venv](#working-in-a-virtual-environment).

The virtual environment will use the Python executable that was used to set it up with `-m venv`. Thus, if you create a venv with a certain version of Python, this version is the one that will be used inside the venv. For example, to set up the same environment as on most of the CI at the time of writing, [install Python 3.5](#installing-different-python-versions) and run
```sh
python3.5 -m venv ~/mbedtls-venv-3.5
~/mbedtls-venv-3.5/bin/python scripts/min_requirements.py
```

Note that the venv directory contains references to its own path, so if you want to move it, you have to do [more than just move the directory](https://stackoverflow.com/questions/32407365/can-i-move-a-virtualenv).

### Working in a virtual environment

In a nutshell: start a new shell (bash, zsh or ksh) and issue this command (where `~/venv-mbedtls-development` is the path to the venv directory, the same path passed to `python -m venv`):
```sh
. ~/venv-mbedtls-development/bin/activate
```

Note the `.` at the beginning: the commands must run inside the running shell, not as a subprogram. There are also `activate` scripts for fish, csh, PowerShell and cmd. The `activate` changes the shell prompt to indicate the active virtual environment.

The `activate` script sets environment variables so that all calls to `python` or `python3` will use the Python installation from the virtual environment, with the packages from the virtual environment.

```console
mbedtls$ . ~/venv-mbedtls-development/bin/activate
(venv-mbedtls-development) mbedtls$ make generated_files
  Gen   error.c
  Gen   version_features.c
  Gen   ssl_debug_helpers_generated.c
  Gen   psa_crypto_driver_wrappers.c
  Gen   psa/psa_constant_names_generated.c
  Gen   test/query_config.c
  Gen   suites/test_suite_psa_crypto_generate_key.generated.data suites/test_suite_psa_crypto_not_supported.generated.data suites/test_suite_psa_crypto_op_fail.generated.data suites/test_suite_psa_crypto_storage_format.current.data suites/test_suite_psa_crypto_storage_format.v0.data ...
  Gen   suites/test_suite_bignum.generated.data suites/test_suite_bignum_core.generated.data
  Gen   visualc/VS2010/mbedTLS.sln ...
(venv-mbedtls-development) mbedtls$ tests/scripts/check-python-files.sh
Running pylint ...

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)


Running mypy ...
Success: no issues found in 27 source files
```

To run a single Python script in the virtual environment, you don't need to use `activate`: you can invoke Python via the symbolic link from the `bin` directory of the virtual environment. This also works with Python programs that are part of the virtual environment. You need `activate` when invoking programs that themselves call Python.

### Installing different Python versions

Each virtual environment can have a different Python version, and running in a virtual environment makes that version of Python the one on the command search path. But all the Python versions need to be installed at the system level.

You can have multiple Python versions installed at the system level, and they won't interfere. Here are a few ways you can install additional Python versions:

* On Ubuntu or other Debian-based distributions: the [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa).
* On Linux: install another Debian or Ubuntu release in a chroot, made painless with [schroot](https://wiki.debian.org/Schroot) and debootstrap.
* On macOS with [Homebrew](https://brew.sh/): e.g. `brew install python3.6`
* On macOS with [MacPorts](https://www.macports.org/): e.g. `sudo port install py36`
* On macOS with [Fink](https://www.finkproject.org/): e.g. `fink install python36`
* On most systems except Windows, with [pyenv](https://github.com/pyenv/pyenv).
* On most systems, with [Conda](https://docs.conda.io/en/latest/).
