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

epic = "Mbed TLS 3.6 release"       # Name of epic that needs to be moved
                                    # (It needs to match an empty epic on v2 board)
closed_after_date = "2023-10-01"    # Only include entries closed after that date

max_entries = 500                   # How many maximum entries the backend will populate.
debug = False                       # Set to True to print out the github cli commands.

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

projectv2_project_past_epics = "PVT_kwDOBcuPHc4AgPo7"
projectv2_field_status = "PVTSSF_lADOBcuPHc4AgPo7zgVai1o"
projectv2_field_owner = "Mbed-TLS"
projectsv1_repo = "Mbed-TLS/mbedtls"
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


def projectv2_get_label_ids(project_id=projectv2_project_past_epics):
    """Use a gql querry to retrieve the node-ids for the column names of projectV2 """

    labels = []
    querry = gql_get_ids_querry.substitute(project_uid=project_id)
    result = github_querry(querry)
    # clean up the result
    nodes = [n for n in result["data"]["node"]["fields"]["nodes"] if n]
    return nodes.pop()["options"]


####################### Github Cli Wrappers #########################
def get_issues_prs_for_project_v1(issues=True,
                                  from_date=closed_after_date,
                                  count=max_entries,
                                  repo=projectsv1_repo):
    """ Retrieve a maximum n=count number issues or pull requests closed after a date """

    cmd = ("gh {0} --repo {3} list -L {1} -s all --search \"is:{0} is:closed "
           "closed:>{2}\"  --json 'number,projectCards'").format("issue" if issues else "pr",
                                                                 count, from_date,
                                                                 repo)
    ret = do_shell_exec(cmd)
    data = json.loads(ret.stdout)
    data = [n for n in data if n["projectCards"]]
    data = [{n["number"]: n["projectCards"]} for n in data]
    return data


def get_issues_prs_for_name_for_project_v1(column_name,
                                           project_name=active_project,
                                           count=max_entries):
    """ Retrieve all issues AND pull requests under a column of a projectv1 """

    output = {"epic": column_name,
              "issues": [], "prs": []}

    issues = get_issues_prs_for_project_v1(count=count)

    for n in issues:
        for issue_num, issue_proj_list in n.items():
            # An item can have multiple projects assosiated with it.
            for issue_proj in issue_proj_list:
                n_pname = issue_proj["project"]["name"]
                n_cname = issue_proj["column"]["name"]
                # Matches the expected project board
                if n_pname == project_name and n_cname == column_name:
                    output["issues"].append(str(issue_num))
                else:
                    continue

    prs = get_issues_prs_for_project_v1(issues=False, count=count)
    for n in prs:
        for issue_num, issue_proj_list in n.items():
            # An item can have multiple projects assosiated with it.
            for issue_proj in issue_proj_list:
                n_pname = issue_proj["project"]["name"]
                n_cname = issue_proj["column"]["name"]
                # Matches the expected project board
                if n_pname == project_name and n_cname == column_name:
                    output["prs"].append(str(issue_num))
                else:
                    continue
    return output


def get_no_status_issues_prs_for_project_v2(count=100):
    """ Get the contents for the No Status Column in project v2 """

    cmd = "gh project item-list --owner {} {} -L {} --format json".format(
        projectv2_field_owner, archive_project_board_no, count)

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


def move_issue_to_proj(issue, old_proj, new_proj, is_pr=False, repo=projectsv1_repo):
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


def move_to_column_project_v2(item_node_id,
                              column_node_id,
                              field_node_id=projectv2_field_status,
                              project_node_id=projectv2_project_past_epics):
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
                issue,
                old_proj,
                old_proj))


if __name__ == "__main__":

    # Do not proceed if an empty epic has not been created
    label_matches = [n for n in projectv2_get_label_ids() if n["name"] == epic]

    if not label_matches:
        print(
            "Error, please create an epic with name \"{}\" and re-run. ".format(epic))
        sys.exit(1)

    # Extract the node_id if for the match
    column_node_id = label_matches[0]["id"]

    # Querry all the items (prs and issues)
    epic_items = get_issues_prs_for_name_for_project_v1(epic)
    epic_name = epic_items["epic"]
    epic_issues = epic_items["issues"]
    epic_prs = epic_items["prs"]

    # Ask for user confirmation
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
    no_stat_isues = get_no_status_issues_prs_for_project_v2()

    # Move them to the matching epic
    for pr_no, node_id in no_stat_isues.items():
        move_to_column_project_v2(node_id, column_node_id)
        print("Moving {} to {}".format(pr_no, epic))