# Mbed TLS script coding standards

## General conventions for scripts

### Choice of scripting language

The preferred language for scripts in the Mbed TLS project is Python. Use Python for new scripts that are committed to the project unless there's a good reason.

Some reasons not to use Python:

* A script that only applies to Windows and should ideally work out of the box can be written in cmd.
* Some CI code in the [`mbedtls-test` repository](https://github.com/Mbed-TLS/mbedtls-test) is written in Groovy, for its Jenkins integration.
* A script only intended for the Mbed TLS developers, and whose job is mostly to run other programs, can be written in sh.
* If you're extending existing scripts, then obviously keep using the same language.
* Throwaway scripts that do ad hoc automated refactoring (e.g. renaming identifiers) are often in Perl, thanks to its convenient text manipulation primitives.

### Language versions

Check [`README.md`](https://github.com/Mbed-TLS/mbedtls/blob/development/README.md#tool-versions) for the current minimum supported version of Python and other tools. Note that in addition to the public commitments, at any given time, there may be additional constraints due to the platforms on which we run automated tests. As of September 2022, Python scripts must be compatible with Python 3.5.

For scripts that need to be backported, note that [long-time support branches](https://github.com/Mbed-TLS/mbedtls/blob/development/BRANCHES.md#long-time-support-branches) may support older versions of Python and other tools than the `development` branch.

### Script naming conventions

* Use lowercase names.
* Use either underscores or hyphens to separate words. Python modules that are imported by other scripts cannot use hyphens.
* Perl scripts have a `.pl` extension. Python scripts have a `.py` extensions. Sh and bash scripts have a `.sh` extension. This helps on Windows.

### Invocation conventions

Scripts should be able to run from the root of the Mbed TLS source tree. Support for running from a subdirectory is a plus.

Scripts should run out of the box on a typical Unix-like system if possible. If the script requires some environment variables, try to set sensible defaults.

All scripts should start with a comment that explains the purpose of the script and details of how to use it.
All scripts should print at least a summary explanation of how to invoke the script, including a list of supported options, when invoked with `--help` as an argument.

Scripts should follow Unix conventions for options: `-x` for single-letter option, `--long-option` for options with longer names.

### File structure

All executable scripts committed into the repository should have the following structure:

* The first line is a [shebang line](https://en.wikipedia.org/wiki/Shebang_(Unix)), e.g. `#!/usr/bin/env python3`.
* A brief description of the file (either as a comment or as a string).
* Copyright notice and license indication.
* Initialization code.
* Auxiliary functions (unless the script is so simple it doesn't need any).
* Code that performs the script's purpose (this can be as simple as calling a `main` function, or more complex).

## Python coding standards

### Directory structure

Non-executable Python modules are in `scripts/mbedtls_dev`.
Executable Python scripts in `scripts` can use auxiliary modules with `from mbedtls_dev import ...`.

Executable Python scripts in `tests/scripts` cannot refer to modules in `scripts/mbedtls_dev` directly, because we do not assume that `PYTHONPATH` contains the Mbed TLS source tree. To use other Python modules from a script in `tests/scripts`, use the following idiom:

```python
import scripts_path # pylint: disable=unused-import
from mbedtls_dev import ...
```

### Python imports

We follow the usual convention that imports go at the top of a file (after the docstring and the license comment). Imports are typically ordered as follows:

1. Standard library, in lexicographic order.
2. Third-party libraries, if any, in lexicographic order.
3. Modules from `mbedtls_dev`, in lexicographic order.

Avoid importing individual names from modules, as it can be difficult to figure out which module an unqualified name comes from. However, it's ok to import names if they're sufficiently recognizable, for example:

* Importing individual modules from `mbedtls_dev` is fine.
* Importing capitalized type names from `typing` is fine.
* Importing individual submodules from Cryptodome is fine.

### Third-party Python libraries

Avoid bringing in new dependencies, because each dependency adds risk to the project. Only use dependencies if they have a clear advantage.

The minimum supported version of third-party Python libraries is recorded in `*.requirements.txt` files in the [`scripts` directory](https://github.com/Mbed-TLS/mbedtls/tree/development/scripts). As with the [Python version](#language-versions), keep in mind that long-time support branches may need to support older versions.

### Python language features

The maintainers of Mbed TLS are primarily C programmers, not Python programmers. It's ok to use fancy language features if they make the code significantly simpler, but don't necessarily assume that the reader is familiar with them. Make sure that unfamiliar readers can easily look up such fancy features.

* Classes, methods and simple inheritance can be used freely.
* Avoid metaclasses and nontrivial dynamic class creation. If you use these features, write documentation that's accessible to non-experts.
* Do define [special methods](https://docs.python.org/3/reference/datamodel.html#special-method-names) if convenient for comparison, context managers, etc. But avoid customizing attribute access.
* Use [decorators](https://docs.python.org/3/glossary.html#term-decorator) if they have a clear benefit.
* Do use [generators](https://docs.python.org/3/glossary.html#term-generator) and [list comprehension](https://docs.python.org/3/glossary.html#term-list-comprehension) where warranted.

### Python typing

Using type annotations is encouraged. We run [mypy](http://mypy-lang.org/) to verify static typing.

Avoid complex overloading. It's generally easier to understand code if it only expects a specific type of data.

### Python style conventions

We generally follow [PEP 8](https://peps.python.org/pep-0008/), and [PEP 257](https://peps.python.org/pep-0257/) for docstrings.

### Python style enforcement

We run [Pylint](https://pylint.pycqa.org/) for style enforcement. Pylint is quite opinionated sometimes, so if a rule doesn't make sense in a specific context, use a [Pylint pragma comment](https://pylint.pycqa.org/en/latest/user_guide/messages/message_control.html) to disable it.
