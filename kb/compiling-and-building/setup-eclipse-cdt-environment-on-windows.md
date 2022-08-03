# Setting up the Eclipse CDT environment on Windows

## Introduction

This quick start manual is intended for C/C++ developers who are interested in developing Mbed TLS-based projects in Eclipse C/C++ Development Tool (CDT) on Windows.

## Software versions used in this tutorial

* Eclipse C/C++ Development Tool (CDT) Juno SR1.
* Cygwin packages:
  * **C compiler:** `gcc-core (3.4.4-999)`.
  * **C++ compiler:** `gcc-g++ (3.4.4-999)`.
  * **GNU Debugger:** `gdb (7.5.50-1)`.
  * **Make utility:** `make (3.82.90-1)`.

Your experience may differ based on the software versions you use.

## Install Cygwin or MinGW

We recommend Cygwin, so this tutorial doesn't cover the MinGW installation. For more on MinGW, look at [Compiling Mbed TLS in MinGW](/kb/compiling-and-building/compiling-mbedtls-in-mingw).

  * Download and install Cygwin by following the first three steps in the [tutorial](http://www3.ntu.edu.sg/home/ehchua/programming/howto/cygwin_howto.html). Make sure that you select `gcc`, `g++`, `gdb`, and `make` packages under the `Devel` (Development) category, since these packages are not part of the default installation.

  * Add  `C:\cygwin\bin` to your **PATH Environment Variables**.

  * If you want to check if all needed packages are installed, run the Cygwin Terminal and type `cygcheck -c`.

## Install Eclipse C/C++ Development Tool (CDT)

You can either download and install a new version of Eclipse CDT, or extend the existing **Eclipse for Java Developers** on your system with a CDT plugin.

**Option 1:** Clean Eclipse CDT install:
  * [Download](http://www.eclipse.org/downloads) **Eclipse IDE for C/C++ Developers** and unzip the downloaded file into a directory of your choice.
  * Run `eclipse.exe` inside the directory.

**Option 2:** Extend an existing **Eclipse for Java Developers** installation:
 * Launch Eclipse.
 * Go to **Help** > **Install New Software**.
 * In "Work with", enter the CDT update site `http://download.eclipse.org/tools/cdt/releases/juno` (for Eclipse Juno only) > **Add** > Enter a name (such as CDT 8.1.0) > Select **all the "CDT main features"**.
 * You may select optional features.
 * Click **Finish**.
 * Restart Eclipse after the plugin installation is finished.

<!--- "This quickstart manual is intended for C/C++ developers who are interesting in developing Mbed TLS based projects in Eclipse C/C++ Development Tool (CDT) on Windows.","Eclipse CDT, Cygwin, Eclipse installation","eclipse, cygwin, tutorial",published,"2013-01-04 15:39:00",6,47375,"2015-07-24 11:51:00","Paul Bakker"--->
