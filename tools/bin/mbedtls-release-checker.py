#!/usr/bin/env python3
#
# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script attempts to analyse a release and its associated LTS releases, and link up the relevant
backport PRs as well as highlighting PRs with missing changelog entries.

In order to run this you must have GH Cli https://cli.github.com installed and authorised to act as
you on github.

In order to get a GH Cli auth token, either run 'gh auth' or EXPORT $GITHUB_TOKEN (see
https://cli.github.com/manual/gh_auth_login for further details).

Suggested use:

Checkout and create local branches for the releases you want to check, then run with eg:

release-checker.py development-local mbedtls.prev.release mbedtls-lts mbedtls.prev.lts.release

where mbedtls.prev.release and mbedtls.prev.lts.release are tags created by the previous release
process. Any locally available tag or branch or hash will work here.

TODO:

- This will incorrectly pick up the merge back PRs, if the restricted PR number matches one in
  development. These need to be filtered out somehow, for now if there are any PRs with a number way
  off the rest of the PRs in the release, ignore it.
- Needs slight alteration to allow for an arbitrary number of LTS releases linked to a development
  release.

"""

import argparse
import json
import csv
from traceback import format_exc
import re

from subprocess import Popen, PIPE
from shlex import split

import logging
from sys import stdout

MBEDTLS_MAIN_REPOSITORY = 'Mbed-TLS/mbedtls'
MBEDTLS_RESTRICTED_REPOSITORY = 'Mbed-TLS/mbedtls-restricted'

class AppError (Exception):

    """
    Basic custom exception type to throw, with error message
    """

    def __init__(self, message="Unknown app error occurred"):
        self.message = message
        super().__init__(self.message)

    def GetMessage(self):
        return self.message


class ShellExecResult:

    """
    Class to encapsulate the returns from a shell execution.
    """

    def __init__(self, success, stdout, stderr):

        self.success = success
        self.stdout = stdout
        self.stderr = stderr

def do_shell_exec(exec_string, expected_result = 0):

    """
    Helper function to do shell execution
    exec_string     - String to execute (as is - function will split)
    expected_result - Expected return code.
    """

    shell_process = Popen(split(exec_string), stdin=PIPE, stdout=PIPE, stderr=PIPE)

    (shell_stdout, shell_stderr) = shell_process.communicate()

    return ShellExecResult(shell_process.returncode == expected_result,
                           shell_stdout.decode("utf-8"),
                           shell_stderr.decode("utf-8"))

class GitHubPR:

    """
    Class to encapsulate a single Github PR
    """

    def __init__(self, logger, github_repo, hash, pr_number, data):
        """
        Constructor
        logger      - Logging class
        github_repo - Github Org / Project for this PR.
        hash        - Git hash of merge commit.
        pr_number   - Index of github pull request that caused the merge commit.
        data        - Json data for PR, returned from GH cli.
        """
        self.logger = logger
        self.github_repo = github_repo
        self.hash = hash;
        self.pr_number = pr_number;
        self.title = data["title"]
        self.body = data["body"]

        self.has_changelog = False
        self.is_backport = False

        self.requires_backport = False

        self.changelog_check = False
        self.backport_check = False
        self.tests_check = False

        self.linked_prs = []

        self.backport_of = ""
        self.backport = ""

        self.parse_data(data)


    def parse_data(self, data):

        """
        Parse the received data into class local variables.
        data - Json data for PR, returned from GH cli.
        """

        for file in data["files"]:
            if file["path"].find("ChangeLog.d") != -1:
                self.has_changelog = True
                break

        if re.search('backport', self.title, re.IGNORECASE) or \
            re.search('backport of', self.body, re.IGNORECASE):
            self.is_backport = True

        for label in data["labels"]:
            if label["name"] == 'needs-backports':
                self.requires_backport = True

        # search body for linked prs. Note, not checking the comments for linked PRs at this time.
        linked_prs = re.findall('(?<=#)\d+', self.body)

        link_search_string = '(?<={})\d+'.format(self.get_github_link_base())
        linked_prs += re.findall(link_search_string, self.body)

        # remove duplicates.
        for link_pr in linked_prs:
            if link_pr not in self.linked_prs:
                self.linked_prs.append(link_pr)

        # Look for the check boxes. Note that the box being checked can either mean that the thing
        # has been provided, or is not required.
        self.changelog_check = self.get_checkbox_state('changelog')
        self.backport_check = self.get_checkbox_state('backport')
        self.tests_check = self.get_checkbox_state('tests')

        self.logger.log(logging.INFO, "Adding {} : PR {} : {}".format(self.hash, self.pr_number,
                                                                      self.title))

    def get_checkbox_state(self, checkbox_string):

        """
        Helper to get the checkbox states from the PR template body.
        """

        search_string = '(?<=\[)(.*)(?=] \W*{})'.format(checkbox_string)

        check_match = re.search(search_string, self.body, re.IGNORECASE)

        if check_match:
            if check_match.group() == 'x' or check_match.group() == 'X':
                return True
            else:
                self.logger.log(logging.DEBUG, 'Check box contained oddness : {}'.format(check_match.group()))
        else:
            self.logger.log(logging.DEBUG, 'Check box string not found')

        return False

    def has_linked_pr(self, pr_number):

        return pr_number in self.linked_prs

    def get_github_link_base(self):
        return 'https://github.com/{}/pull/'.format(self.github_repo);

    def get_github_link(self):
        return self.get_github_link_base() + self.pr_number

class Release:

    def __init__(self, logger, github_repo, start_range, end_range, is_LTS):

        """
        Constructor
        logger      - Logging class
        github_repo - Github Org/Project for this release.
        start_range - Git hash / label etc defining start of range
        end_range   - Git hash / label etc defining start of range
        is_LTS      - True if this release is an LTS release
        """

        self.github_prs = {}

        self.logger = logger
        self.github_repo = github_repo
        self.start_range = start_range;
        self.end_range = end_range;
        self.is_LTS = is_LTS

        self.get_prs_for_range(start_range, end_range)

    def get_prs_for_range(self, start_range, end_range):

        """
        Get all PRs (merge commits) within a given git range (usually defining a release)
        start_range - Git hash / label etc defining start of range
        end_range   - Git hash / label etc defining start of range
        """

        result = do_shell_exec(
            'git log --merges --first-parent --format=\"%H %s\" {}...{} '.format(start_range,
                                                                                 end_range))

        if not result.success:
            raise AppError("git log failed : {}".format(result.stderror))

        for line in result.stdout.splitlines():
            line_split = line.split(maxsplit=1)

            hash = line_split[0]
            subject = line_split[1]

            if not subject.startswith('Merge pull request'):
                self.logger.log(logging.WARNING,
                                'Ignoring {} as non-PR commit subject : {}'.format(hash, subject))
                continue;


            pr_number_match = re.search('(?<=#)\d+', subject);

            if pr_number_match is None:
                self.logger.log(logging.WARNING,
                                'Ignoring {} as no PR in subject : {} '.format(hash, subject))
                continue;

            pr_number = pr_number_match.group()

            # Use of --repo here hopefully saves us in situations where gh cli has not been
            # setup (you still need to either set GITHUB_TOKEN or run gh auth login)
            result = do_shell_exec(
                "gh pr view --repo {} --json title,body,mergeCommit,files,labels {}".format(self.github_repo,
                                                                                            pr_number))

            if not result.success:
                # This is likely the mergeback commit, which comes from another repo, ignore
                # it.
                if(result.stderr.startswith('GraphQL: Could not resolve to a PullRequest')):
                    self.logger.log(logging.WARNING,
                                    'Ignoring {} as could not resolve PR {} (other repo?)'.format(hash,
                                                                                                  pr_number))
                    continue;
                else:
                    raise AppError("gh pr view failed : {}".format(result.stderr))

            data = json.loads(result.stdout);

            self.github_prs[pr_number] = GitHubPR(self.logger, self.github_repo, hash,
                                                  pr_number, data)

    def get_pr(self, pr_number):

        if pr_number in self.github_prs:
            return self.github_prs[pr_number]
        else:
            return None

    def link_backports(self, other_release):

        """
        Attempt to link backports between this and another release
        other_release   - release to attempt to link with.
        """

        # Safety. One side of the link should be LTS, one side not.
        if self.is_LTS and other_release.is_LTS:
                raise AppError("Cannot link two LTS releases.")

        if not self.is_LTS and not other_release.is_LTS:
                raise AppError("Cannot link two development releases.")

        for hash, pr in self.github_prs.items():

            if self.is_LTS:
                # Attempt to find the original PRs for my backports.
                if pr.is_backport and pr.backport_of == "":
                    for link_pr in pr.linked_prs:
                        target_link_pr = other_release.get_pr(link_pr)
                        if target_link_pr != None:
                            if target_link_pr.requires_backport or target_link_pr.has_linked_pr(pr.pr_number):
                                if target_link_pr.backport != "":
                                    self.logger.log(logging.WARNING,
                                                    "PR {} links to PR {}, but PR {} already has a backport {}".format(pr.pr_number, \
                                                                                                                       target_link_pr.pr_number, \
                                                                                                                       target_link_pr.pr_number, \
                                                                                                                       target_link_pr.backport))
                                else:
                                    pr.backport_of = target_link_pr.pr_number
                                    target_link_pr.backport = pr.pr_number

                                    self.logger.log(logging.INFO,
                                                    "Linking {} as backport of {}".format(pr.pr_number,
                                                                                          target_link_pr.pr_number))

                                    if not pr.is_backport:
                                        pr.is_backport = True
                                        self.logger.log(logging.INFO,
                                                        "Forcing {} to be backport on link".format(pr.pr_number))
                                break
            else:
                # Attempt to find backports of my PRs
                if  pr.backport == "":
                    for link_pr in pr.linked_prs:
                        target_link_pr = other_release.get_pr(link_pr)
                        if target_link_pr != None:
                            if target_link_pr.is_backport or target_link_pr.has_linked_pr(pr.pr_number):
                                if target_link_pr.backport_of != "":
                                    self.logger.log(logging.WARNING,
                                                    "PR {} links to PR {}, but PR {} already is a backport of {}".format(pr.pr_number, \
                                                                                                                         target_link_pr.pr_number, \
                                                                                                                         target_link_pr.pr_number, \
                                                                                                                         target_link_pr.backport_of))
                                else:
                                    pr.backport = target_link_pr.pr_number
                                    target_link_pr.backport_of = pr.pr_number

                                    self.logger.log(logging.INFO,
                                                    "Linking {} as backport of {}".format(target_link_pr.pr_number,
                                                                                          pr.pr_number))

                                    if not target_link_pr.is_backport:
                                        target_link_pr.is_backport = True
                                        self.logger.log(logging.INFO,
                                                        "Forcing {} to be backport on link".format(target_link_pr.pr_number))
                                break

    def get_cvs_link(self, link_target, link_text = ''):

        if link_text == '':
            return '\"=HYPERLINK(\"{}\")\"'.format(link_target)
        else:
            return '=HYPERLINK(\"{}\",\"{}\")'.format(link_target, link_text)


    def write_csv(self, file_name):

        self.logger.log(logging.INFO, 'Writing CSV file to {}'.format(file_name))

        header_fields = ['Hash', 'PR Number', 'Title', 'Is Backport', 'Has Changelog',
                         'Changelog Check', 'Backport Check', 'Tests Check', 'Backport Link',
                         'Linked PRs+']

        with open(file_name, 'w') as csv_file:

            csv_writer = csv.writer(csv_file)

            csv_writer.writerow(header_fields)

            for hash, pr in self.github_prs.items():

                backport_num = pr.backport_of if pr.is_backport else pr.backport

                if backport_num == '':
                    backport = 'None'
                else:
                    backport = self.get_cvs_link('https://github.com/{}/pull/{}'.format(self.github_repo,
                                                                                        backport_num),
                                                 backport_num)

                csv_row = [pr.hash, self.get_cvs_link(pr.get_github_link(), pr.pr_number),
                           pr.title, pr.is_backport, pr.has_changelog, pr.changelog_check,
                           pr.backport_check, pr.tests_check, backport]

                linked_prs = ''
                first = True

                for link_pr in pr.linked_prs:
                    csv_row.append(self.get_cvs_link('https://github.com/{}/pull/{}'.format(self.github_repo,
                                                                                            link_pr),
                                                     link_pr))

                csv_writer.writerow(csv_row)

def main():

    parser = argparse.ArgumentParser(description='Attempt to automatically detect missing backports/Changelog entries for an MbedTLS release')
    parser.add_argument('LTS_range_start', help='Git hash/label of LTS branch range start')
    parser.add_argument('LTS_range_end', help='Git hash/label of LTS branch range start')
    parser.add_argument('dev_range_start', help='Git hash/label of development branch range start')
    parser.add_argument('dev_range_end', help='Hash/label of development branch range end')
    parser.add_argument('-lo', '--LTS_output', help='Ouput file to dump LTS release csv data to')
    parser.add_argument('-do', '--dev_output', help='Ouput file to dump development release csv data to')
    parser.add_argument('-r', '--restricted', action='store_true', help='Use restricted repository')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable extra logging')
    parser.add_argument('-vv', '--veryverbose', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    logger = logging.getLogger("release-checker")

    log_handler = logging.StreamHandler(stdout)
    if args.veryverbose:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    log_handler.setFormatter(logging.Formatter("%(levelname)s : %(message)s"));
    logger.addHandler(log_handler)

    try:

        github_repo = MBEDTLS_RESTRICTED_REPOSITORY if args.restricted else MBEDTLS_MAIN_REPOSITORY

        logger.log(logging.INFO, "Adding LTS range : {} -> {}".format(args.LTS_range_start,
                                                                      args.LTS_range_end))
        LTS_release = Release(logger, github_repo, args.LTS_range_start, args.LTS_range_end, True)
        logger.log(logging.INFO, "Adding dev range : {} -> {}".format(args.dev_range_start,
                                                                      args.dev_range_end))
        dev_release = Release(logger, github_repo, args.dev_range_start, args.dev_range_end, False)

        dev_release.link_backports(LTS_release)
        LTS_release.link_backports(dev_release)

        if args.dev_output:
           dev_release.write_csv(args.dev_output)
        if args.LTS_output:
           LTS_release.write_csv(args.LTS_output)

    except AppError as e:
        logger.log(logging.CRITICAL, e.GetMessage())

    except:
        logger.log(logging.CRITICAL, format_exc())

    finally:
        logger.log(logging.INFO, "### Script done.")

if __name__ == "__main__":
    exit(main())
