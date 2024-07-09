"""Create a simple artifact sign and verify server."""

# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
#

# The script assumes that gpg agent caching is
# disabled. The password provided by the user is used to confirm
# that the user is authorised to sign the files.

# Please configure gpg-agent with `max-cache-ttl 0` when deploying.
# Run as MBEDTLS_FW_SIGN_SERVER_IP=X.X.X.X && python artifact_sign.py

import random
import os
import string
import shlex
import shutil
import subprocess
import pathlib
from typing import Tuple

import flask
################  /* Configuration Parameters  #################
APP = flask.Flask(__name__)

# Allow the host to set the IP for the server3
SERVER_IP = "0.0.0.0"        # Will launch the server but dl links won't work.
SERVER_PORT = "5000"         # Port to bind to.
CLEANUP_ON_STARTUP = True    # Cleanup the temporary directory on launch.

################  Configuration Parameters */  #################

# ENV overrides
if "MBEDTLS_FW_SIGN_SERVER_IP" in os.environ:
    SERVER_IP = os.environ["MBEDTLS_FW_SIGN_SERVER_IP"]

if "MBEDTLS_FW_SIGN_SERVER_PORT" in os.environ:
    SERVER_PORT = os.environ["MBEDTLS_FW_SIGN_SERVER_PORT"]

DOWNLOAD_PFIX = "http://{}:{}/".format(SERVER_IP, SERVER_PORT)
SIGN_CMD = ("gpg --detach-sign --pinentry-mode loopback"
            " --passphrase '{pasw}' --armor --batch {tarb}")
VERIFY_CMD = "gpg --verify {sig} {tarb}"
SUM_CMD = "sha256sum {tarb}"
ZIP_CMD = "zip -r {name}.zip ."


def do_shell_exec(exec_string: str) -> Tuple[int, str, str]:
    """Helper function to do shell execution.

    exec_string     - String to execute (as is - function will split)
    expected_result - Expected return code.
    """

    shell_process = subprocess.Popen(
        shlex.split(exec_string),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    (shell_stdout, shell_stderr) = shell_process.communicate()

    return (shell_process.returncode,
            shell_stdout.decode("utf-8"),
            shell_stderr.decode("utf-8"))


def randomise_path(name: str) -> str:
    """Attach a pseudo-ranom postfix of an underscore and 3 uppercase characters."""
    pfix = "".join(random.choices(string.ascii_uppercase, k=3))
    return os.path.join("tmp", "{}_{}".format(name, pfix))


@APP.route('/')
def main() -> flask.typing.ResponseReturnValue:
    """Invoked on main landing page."""
    return flask.render_template("index.html")


@APP.route('/<path>/<filename>')
def download(path: str, filename: str) -> flask.typing.ResponseReturnValue:
    """Invoked on {SERVERIP:PORT}/tmp_workdir/filename api endpoint."""
    path = os.path.join("tmp", path)
    return flask.send_from_directory(path, filename, as_attachment=True)

# pylint: disable=too-many-locals, inconsistent-return-statements
@APP.route('/sign', methods=['POST'])
def sign() -> flask.typing.ResponseReturnValue:
    """Invoked on {SERVERIP:PORT}/sign api endpoint."""
    if flask.request.method == 'POST':

        # Accept the file
        f = flask.request.files['rel_file']
        f.save(f.filename)

        pwd = flask.request.form.get("passw")

        # Update the names with the new tmp directory
        artf_name = f.filename
        artf_basename = artf_name.split(".")[0]
        sha_fname = artf_name + ".sha256.txt"
        sign_fname = artf_name + ".asc"
        tmp_workdir = randomise_path(artf_basename)

        if CLEANUP_ON_STARTUP:
            shutil.rmtree(tmp_workdir, ignore_errors=True)
        archive_name = artf_basename + ".zip"

        # Create a workdir
        pathlib.Path(tmp_workdir).mkdir(parents=True, exist_ok=True)

        artf_name = os.path.join(tmp_workdir, artf_name)
        sha_fname = os.path.join(tmp_workdir, sha_fname)
        sign_fname = os.path.join(tmp_workdir, sign_fname)
        archive_name = os.path.join(tmp_workdir, archive_name)

        # Move the tarballs
        os.rename(f.filename, artf_name)

        # Calculate the sha256
        ret_code, _stdout, _sterr = do_shell_exec(SUM_CMD.format(tarb=artf_name))
        if ret_code == 0:
            with open(sha_fname, "w") as sha_file:
                sha_file.write(_stdout)
            sha = shlex.split(_stdout)[0]
        else:
            raise Exception("Shasum failed!")

        # Sign the tarball
        ret_code, _stdout, _sterr = do_shell_exec(SIGN_CMD.format(pasw=pwd, tarb=artf_name))
        # If password is incorrect or other error exit.
        if ret_code != 0:
            return flask.render_template("signed.html",
                                         artf_name="Not Authorised",
                                         artf_url=DOWNLOAD_PFIX,
                                         sha="Not Authorised",
                                         sha_url=DOWNLOAD_PFIX,
                                         sign_name="Not Authorised",
                                         sign_url=DOWNLOAD_PFIX,
                                         zip_name="Not Authorised",
                                         zip_url=DOWNLOAD_PFIX)
        # Zip everything
        cwd = os.getcwd()
        os.chdir(tmp_workdir)
        ret_code, _stdout, _sterr = do_shell_exec(
            ZIP_CMD.format(name=artf_basename))
        if ret_code != 0:
            raise Exception("zip Failed")
        os.chdir(cwd)

        # Calculate the download urls
        sha_url = DOWNLOAD_PFIX + "/".join(sha_fname.split("/")[1:])
        artf_url = DOWNLOAD_PFIX + "/".join(artf_name.split("/")[1:])
        sign_url = DOWNLOAD_PFIX + "/".join(sign_fname.split("/")[1:])
        archive_url = DOWNLOAD_PFIX + "/".join(archive_name.split("/")[1:])

        # Return the results page
        return flask.render_template("signed.html",
                                     artf_name=os.path.basename(artf_name),
                                     artf_url=artf_url,
                                     sha=sha, sha_url=sha_url,
                                     sign_name=os.path.basename(sign_fname),
                                     sign_url=sign_url,
                                     zip_name=os.path.basename(archive_name),
                                     zip_url=archive_url)


@APP.route('/verify', methods=['POST'])
def verify() -> flask.typing.ResponseReturnValue:
    """Invoked on {SERVERIP:PORT}/verify api endpoint."""
    if flask.request.method == 'POST':
        # Create a workdir
        tmp_workdir = randomise_path("verification")
        pathlib.Path(tmp_workdir).mkdir(parents=True, exist_ok=True)

        # Accept the files
        f = flask.request.files['rel_file']
        f.save(f.filename)

        s = flask.request.files['sig_file']
        s.save(s.filename)

    artf_fname = os.path.join(tmp_workdir, f.filename)
    sig_fname = os.path.join(tmp_workdir, s.filename)

    # Move the files
    os.rename(f.filename, artf_fname)
    os.rename(s.filename, sig_fname)

    # Verify the archive's signature
    ret_code, _stdout, _sterr = do_shell_exec(
        VERIFY_CMD.format(sig=sig_fname, tarb=artf_fname))
    verified = "Success" if ret_code == 0 else "Failed"

    # Return the result
    return flask.render_template("verification.html",
                                 verified=verified,
                                 result=_sterr)

if __name__ == '__main__':
    APP.run(host=SERVER_IP, debug=False)
