#!/usr/bin/env python3
""" Assist with the transition of a projectv1 to a projectv2. 
    This is currently used for management purposes and archiving EPICS.

    It will only move public issues/pr's that have been closed/merged.

    Requires a fully woking gh cli https://cli.github.com/ set-up
    and an access token with the appropriate permissions.    
"""
# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License") you may
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

import os
import sys
import json
import requests
from shlex import split
from string import Template
from subprocess import Popen, check_output, PIPE
from pprint import pprint

token = os.environ['GITHUB_TOKEN']


######################### User Config ###########################
# Instuctions
# - Please ensure that your github cli token is present in your enviroment
# - Set the epic name to tranfer here.
# - Create the epic column to the arhive board, matching the src name.
# - If needed adjust the closed_after date to be in a resonable window
# - Fine tune max entries selection if some entries are missing.
# - Private issues and drafts are not picked up by the script.

epic = "3.6.1 patch release"       # Name of epic that needs to be moved
                                    # (It needs to match an empty epic on v2 board)
closed_after_date = "2024-01-01"    # Only include entries closed after that date

max_entries = 500                   # How many maximum entries the backend will populate.
debug = True                       # Set to True to print out the github cli commands.

############################# Constants #############################
"""
The following values should remain the same across the project.
If need to modify them, they can querried as follows:

gh project list --owner Mbed-TLS number 13
    NUMBER  TITLE                      STATE  ID
    13      Past EPICs                 open   PVT_kwDOBcuPHc4AgPo7

gh project --owner Mbed-TLS field-list 13
    NAME                  DATA TYPE                   ID
    Status                ProjectV2SingleSelectField  PVTSSF_lADOBcuPHc4AgPo7zgVai1o

"""
project_epics_for_mbedtls = "PVT_kwDOBcuPHc4AnF0W"
project_past_epics = "PVT_kwDOBcuPHc4AgPo7"
project_field_status = "PVTSSF_lADOBcuPHc4AgPo7zgVai1o"
project_field_owner = "Mbed-TLS"

projects_repo = "Mbed-TLS/mbedtls"
active_project = "EPICs for Mbed TLS"
archive_project = "Past EPICs"
archive_project_board_no = "13"

############################ Github Cli gap #########################
""" This snippet is covering functionality missing for the current version of github cli.
    We need to querry the node-id for the Status SingleSelectField, since that is used as
    epic name columns. """

gql_get_ids_querry = Template(
    """
  query{
  node(id: "$project_uid") {
    ... on ProjectV2 {
      fields(first: 100) {
        nodes {
          ... on ProjectV2SingleSelectField {
            name options {
              id
              name
            }
          }
        }
      }
    }
  }
}"""
)

########################### Helpers #################################

class ShellExecResult:

    """
    Class to encapsulate the returns from a shell execution.
    """

    def __init__(self, success, stdout, stderr):

        self.success = success
        self.stdout = stdout
        self.stderr = stderr


def do_shell_exec(exec_string, expected_result=0):
    """
    Helper function to do shell execution
    exec_string     - String to execute (as is - function will split)
    expected_result - Expected return code.
    """

    if debug:
        print("CMD", exec_string)
    shell_process = Popen(
        split(exec_string),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE)

    (shell_stdout, shell_stderr) = shell_process.communicate()

    return ShellExecResult(shell_process.returncode == expected_result,
                           shell_stdout.decode("utf-8"),
                           shell_stderr.decode("utf-8"))


def github_querry(query, token=token):
    """ Create an authenticated querry to github"""

    request = requests.post('https://api.github.com/graphql',
                            json={'query': query},
                            headers={"Authorization": "token " + token})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed with code {}. Query: {}".format(
                request.status_code, query))


def project_get_label_ids(project_id=project_past_epics):
    """Use a gql querry to retrieve the node-ids for the column names of projectV2 """

    labels = []
    querry = gql_get_ids_querry.substitute(project_uid=project_id)
    result = github_querry(querry)
    # clean up the result
    nodes = [n for n in result["data"]["node"]["fields"]["nodes"] if n]
    return nodes.pop()["options"]


####################### Github Cli Wrappers #########################
def get_issues_prs_for_project(issues=True,
                               is_closed=True,
                               from_date=closed_after_date,
                               count=max_entries,
                               repo=projects_repo):
    """ Retrieve a maximum n=count number issues or pull requests closed after a date """

    cmd = ("gh {0} --repo {5} list -L {3} -s all --search \"is:{0} is:{1} "
           "{2}:>{4}\"  --json 'number,projectItems'").format("issue" if issues else "pr",
                                                                 "closed" if is_closed else "open",
                                                                 "closed" if is_closed else "created",
                                                                 count, from_date,
                                                                 repo)
    ret = do_shell_exec(cmd)
    data = json.loads(ret.stdout)
    data = [n for n in data if n["projectItems"]]

    data = [{n["number"]: n["projectItems"]} for n in data]
    return data

def link_issues_pr_linked_to_epic(raw_data, epic_name, projectboard = ""):
    """ Parse a raw data output and return a list of items linked to a selected epic."""

    linked = []
    for i in raw_data:
        for k, v in i.items():
            for e in v:
                if epic_name and projectboard:
                    if e["status"]["name"] == epic_name and e['title'] == projectboard:
                        linked.append(k)
                else:
                    if e["status"]["name"] == epic_name:
                        linked.append(k)
    return linked

def get_epic_items(column_name, status="both", projectboard=active_project, repo=projects_repo):
    """ Return a structured data-set containing an epic name and all the open/closed issues in it."""

    output = {"epic": column_name,
              "issues": [], "prs": []}

    if status not in ["open", "closed", "both"]:
        print("Error: Invalid entry for status:", status)
        return
    is_closed = "closed" == status
    issues = get_issues_prs_for_project(issues=True, is_closed=is_closed, repo=repo)
    output["issues"] = link_issues_pr_linked_to_epic(issues, column_name, projectboard)

    prs = get_issues_prs_for_project(issues=False, is_closed=is_closed, repo=repo)
    output["prs"] = link_issues_pr_linked_to_epic(prs, column_name, projectboard)

    # If both is selected just toggle the is_closed state and append the results
    if status == "both":
        is_closed ^=True
        issues = get_issues_prs_for_project(issues=True, is_closed=is_closed, repo=repo)
        output["issues"] +=  link_issues_pr_linked_to_epic(issues, column_name, projectboard)

        prs = get_issues_prs_for_project(issues=False, is_closed=is_closed, repo=repo)
        output["prs"] += link_issues_pr_linked_to_epic(prs, column_name, projectboard)
    return output

def get_no_status_issues_prs_for_project(count=100):
    """ Get the contents for the No Status Column in project v2 """

    cmd = "gh project item-list --owner {} {} -L {} --format json".format(
        project_field_owner, archive_project_board_no, count)

    output = {}
    ret = do_shell_exec(cmd)
    data = json.loads(ret.stdout)

    for entry in data["items"]:
        if "status" not in entry.keys():
            if entry["content"]["type"] == "Issue":
                output[entry["content"]["number"]] = entry["id"]
            else:
                output[entry["content"]["number"]] = entry["id"]
    return output


def move_issue_to_proj(issue, old_proj, new_proj, is_pr=False, repo=projects_repo):
    """ Moves an issue across projects. It works across legacy and v2 projects """

    # Remove the issue from old project
    cmd = "gh {} edit {} --repo {} --{}-project \"{}\"".format(
        "pr" if is_pr else "issue", issue, repo, "remove", old_proj)
    ret = do_shell_exec(cmd)
    if ret.success:
        # #Add it to the new project
        cmd = "gh {} edit {} --repo {} --{}-project \"{}\"".format(
            "pr" if is_pr else "issue", issue, repo, "add", new_proj)
        ret = do_shell_exec(cmd)
        if ret.success:
            print(
                "Successuflly moved issue {} from project: {} -> {}".format(issue, old_proj, new_proj))
        else:
            print(cmd)
            print(
                "Failed to remove issue {} from project: {} sterr: {}".format(
                    issue, old_proj, ret.stderr))
    else:
        print(cmd)
        print(
            "Failed to remove issue {} from project: {} sterr: {}".format(
                issue,
                old_proj,
                ret.stderr))


def move_to_column_project(item_node_id,
                              column_node_id,
                              field_node_id=project_field_status,
                              project_node_id=project_past_epics):
    """ Move an issue/pr by its' node-id on a project v2 project """
    cmd = ("gh project item-edit --id {} --field-id {} --project-id {}  "
          "--single-select-option-id {}").format(item_node_id,
                                                 field_node_id,
                                                 project_node_id,
                                                 column_node_id)
    ret = do_shell_exec(cmd)
    if not ret.success:
        print(
            "Failed to move issue {} sterr: {}".format(
                item_node_id, ret.stderr))

def migrate_epic_to_archive(label_matches):
    """"Contains logic required to move a project to the archives."""
    column_node_id = label_matches[0]["id"]
    print(label_matches)
    epic_items = get_epic_items(epic)
    from pprint import pprint
    epic_name = epic_items["epic"]
    epic_issues = epic_items["issues"]
    epic_prs = epic_items["prs"]

    # Ask for user confirmatwion
    print("Found the following items:")
    print("\nEpic Name:", epic_name)
    print("\nIssues")
    pprint(epic_issues)
    print("\nPRs")
    pprint(epic_prs)

    usr = input("Procceed with move? Y/N?")
    if usr.lower() != "y":
        print("Error, aborting on user request")
        sys.exit(1)

    # Move items to new project
    for issue in epic_issues:
        move_issue_to_proj(issue, active_project, archive_project)

    for pr in epic_prs:
        move_issue_to_proj(pr, active_project, archive_project, is_pr=True)

    # Get the new items by the No Status collumn
    no_stat_isues = get_no_status_issues_prs_for_project()

    # Move them to the matching epic
    for pr_no, node_id in no_stat_isues.items():
        move_to_column_project(node_id, column_node_id)
        print("Moving {} to {}".format(pr_no, epic))

if __name__ == "__main__":

    # Do not proceed if an empty epic has not been created
    label_matches = [n for n in project_get_label_ids() if n["name"] == epic]

    if not label_matches:
        print(
            "Error, please create an epic with name \"{}\" and re-run. ".format(epic))
        sys.exit(1)

    migrate_epic_to_archive(label_matches)


