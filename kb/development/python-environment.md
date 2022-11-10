# Setting up a Python environment for Mbed TLS

## Python and package versions

Each branch of Mbed TLS has different minimum requirements on Python. See `README.md` in the branch. Any Python version that's more recent than the minimum should work, however as of November 2022 this is not well tested by the CI so unintended incompatibilities can happen.

Some of the scripts used by Mbed TLS users and developers require third-party packages. Those have version constraints as well. The constraints are documented via `*.requirements.txt` files in the [`scripts` directory](https://github.com/Mbed-TLS/mbedtls/tree/development/scripts).

We run [mypy](http://mypy-lang.org/) and [pylint](https://pylint.pycqa.org/en/latest/) to check Python scripts. It is common that newer versions of Pylint reject our code, because some checks have become stricter or new checks have been added.

## Set up a Python package environment

### Quick setup

Initial setup:

```sh
python3 -m venv ~/venv-mbedtls-development
~/venv-mbedtls-development/bin/python scripts/min_requirements.py
```

Day-to-day work: start a shell and issue this command:
```sh
. ~/venv-mbedtls-development/bin/activate
```

### Detailed explanations

From any installation of Python, you can set up a [virtual environemnt](https://realpython.com/python-virtual-environments-a-primer/) (“venv” for short) with a specific set of packages. When working in this environment, none of the third-party packages installed globally are visible, so you can have specific versions in this environment without contaminating, or getting contaminated by, your normal system.

Run the following commands from an Mbed TLS checkout to create a virtual environment for that version in the directory `~/venv-mbedtls-development` (which will be created):
```sh
python3 -m venv ~/venv-mbedtls-development
~/venv-mbedtls-development/bin/python scripts/min_requirements.py
```
Use `python -m venv` instead of `python3 -m venv` if that's what your system has. You can also invoke a specific minor version of Python that's installed.

Note that the venv directory contains references to its own path, so if you want to move it, you have to do [more than just move the directory](https://stackoverflow.com/questions/32407365/can-i-move-a-virtualenv).

Now you can run `~/venv-mbedtls-development/bin/python`, `~/venv-mbedtls-development/bin/pylint` and `~/venv-mbedtls-development/bin/mypy` explicitly, and they'll pick up the versions in the virtual environment.

To run scripts that call `python` or other tool in the command search path, use the virtual environment's `activate` script in a shell. This sets up the environment variables needed to use the virtual environment's Python installation instead of the system installation.

For example, in bash, start a new `bash` instance and run the following command:
```sh
. ~/venv-mbedtls-development/bin/activate
```
The same `activate` script works in zsh and ksh as well. There are also `activate.*` scripts for fish, csh and powershell.

Now you can run e.g. `tests/scripts/check-python-files.sh` with the same tool versions as the CI.

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
