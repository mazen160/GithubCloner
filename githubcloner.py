#!/usr/bin/env python3
# coding=utf-8
# *******************************************************************
# *** GithubCloner ***
# * Description:
#   A script that clones public Github repositories
#   of users and organizations automatically.
# * Version:
#   v0.2
# * Homepage:
#   https://github.com/mazen160/GithubCloner
# * Author:
#   Mazin Ahmed <Mazin AT MazinAhmed DOT net>
# *******************************************************************

# Modules
import sys
import os
import time
import json
import threading
import argparse
import requests
import git
import queue


class getReposURLs():
    def __init__(self):
        self.user_agent = "GithubCloner (https://github.com/mazen160/GithubCloner)"
        self.headers = {'User-Agent': self.user_agent, 'Accept': '*/*'}
        self.timeout = 3

    def fromUser(self, user, username=None, token=None):
        """
        Retrieve a list of repositories for a Github user.
        Parameters:
            Required:
                * user: The Github username.
                ** Type: string
        Output:
              * a list of Github repositories URLs.
        """
        URLs = []

        API = "https://api.github.com/users/{}/repos?per_page=40000000".format(user)
        if (username or token) is None:
            resp = requests.get(API, headers=self.headers, timeout=self.timeout).text
        else:
            resp = requests.get(API, headers=self.headers, timeout=self.timeout, auth=(username, token)).text
        resp = json.loads(resp)

        try:
            if (resp["message"] == "Not Found"):
                return([])  # The user does not exist. Returning an empty list.
        except TypeError:
            pass

        for i in range(len(resp)):
            URLs.append(resp[i]["git_url"])

        return(URLs)

    def fromOrg(self, org_name, username=None, token=None):
        """
        Retrieve a list of repositories for a Github organization.
        Parameters:
            Required:
                * org_name: The Github organization name.
                ** Type: string
        Output:
              * a list of Github repositories URLs.
        """
        URLs = []
        API = "https://api.github.com/orgs/{}/repos?per_page=40000000".format(org_name)
        if (username or token) is None:
            resp = requests.get(API, headers=self.headers, timeout=self.timeout).text
        else:
            resp = requests.get(API, headers=self.headers, timeout=self.timeout, auth=(username, token)).text
        resp = json.loads(resp)

        try:
            if (resp["message"] == "Not Found"):
                return([])  # The organization does not exist. Returning an empty list.
        except TypeError:
            pass

        for i in range(len(resp)):
            URLs.append(resp[i]["git_url"])

        return(URLs)

    def fromOrgIncludeUsers(self, org_name, username=None, token=None):
        """
        Retrieve a list of repositories for a Github organization
        and repositories of the Github organization's members.
        Parameters:
            Required:
                * org_name: The Github organization name.
                ** Type: string
        Output:
              * a list of Github repositories URLs.
        """

        URLs = []
        members = []

        URLs.extend(self.fromOrg(org_name, username=username, token=token))

        API = "https://api.github.com/orgs/{}/members?per_page=40000000".format(org_name)
        if (username or token) is None:
            resp = requests.get(API, headers=self.headers, timeout=self.timeout).text
        else:
            resp = requests.get(API, headers=self.headers, timeout=self.timeout, auth=(username, token)).text
        resp = json.loads(resp)

        try:
            if (resp["message"] == "Not Found"):
                return([])  # The organization does not exist. Returning an empty list.
        except TypeError:
            pass

        for i in range(len(resp)):
            members.append(resp[i]["login"])

        for member in members:
            URLs.extend(self.fromUser(member, username=username, token=token))

        return(URLs)

    def checkAuthencation(self, username, token):
        API = "https://api.github.com/user"
        resp = requests.get(API, auth=(username, token), timeout=self.timeout, headers=self.headers)
        if resp.status_code == 200:
            return(True)
        else:
            return(False)

    def fromAuthenticatedUser(self, username, token):
        URLs = []
        API = "https://api.github.com/user/repos?per_page=40000000&type=all"
        resp = requests.get(API, headers=self.headers, timeout=self.timeout, auth=(username, token)).text
        resp = json.loads(resp)

        for i in range(len(resp)):
            URLs.append(resp[i]["git_url"])

        return(URLs)


def cloneRepo(URL, cloningpath, username=None, token=None):
    """
    Clones a single GIT repository.
    Parameters:
        Required:
            * URL: GIT repository URL.
            ** Type: string
            * cloningPath: the directory that the repository will be cloned at.
            ** Type: string
    """

    try:
        try:
            if not os.path.exists(cloningpath):
                os.mkdir(cloningpath)
        except:
            pass
        URL = URL.replace("git://", "https://")
        if (username or token) is not None:
            URL = URL.replace("https://", "https://{}:{}@".format(username, token))
        repopath = URL.split("/")[-2] + "_" + URL.split("/")[-1]
        repopath = repopath.rstrip(".git")
        fullpath = cloningpath + "/" + repopath
        with threading.Lock():
            print(fullpath)
        git.Repo.clone_from(URL, fullpath)
    except Exception as e:
        print("Error: There was an error in cloning [{}]".format(URL))


def cloneBulkRepos(URLs, cloningPath, threads_limit=5, username=None, token=None):
    """
    Clones a bulk of GIT repositories
    Parameters:
        Required:
            * URLs: A list of GIT repository URLs.
            ** Type: list
            * cloningPath: the directory that the repository will be cloned at.
            ** Type: string
        Optional:
            * threads_limit: The limit of threads.
            ** Type: integer
    """
    Q = queue.Queue()
    threads_state = []
    for URL in URLs:
        Q.put(URL)
        while Q.empty() is False:
            if (threading.active_count() < (threads_limit + 1)):
                t = threading.Thread(target=cloneRepo, args=(Q.get(), cloningPath,), kwargs={"username": username, "token": token})
                t.daemon = True
                t.start()
            else:
                time.sleep(0.5)

                threads_state.append(t)
        for _ in threads_state:
            _.join()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user",
                        dest="users",
                        help="Github user (comma-separated input for multiple Github users).",
                        action='store')
    parser.add_argument("-org", "--org",
                        dest="organizations",
                        help="Github organization (comma-separated input for multiple Github organizations).",
                        action='store')
    parser.add_argument("--include-org-members",
                        dest="include_organization_members",
                        help="Include the members of a Github organization.",
                        action='store_true')
    parser.add_argument("-o", "--output-path",
                        dest="output_path",
                        help="The directory to use in cloning Git repositories.",
                        action='store',
                        required=True)
    parser.add_argument("-t", "--threads",
                        dest="threads_limit",
                        help="Threads used in cloning repositories (Default: 5).",
                        action='store',
                        default=5)
    parser.add_argument("-a", "--authentication",
                        dest="authentication",
                        help="Github authentication credentials (username:token).",
                        action='store')
    parser.add_argument("--include-authenticated-repos",
                        dest="include_authenticated_repos",
                        help="Include repositories that the authenticated Github" +
                             " account have access to.",
                        action='store_true')
    args = parser.parse_args()

    users = args.users if args.users else None
    organizations = args.organizations if args.organizations else None
    include_organization_members = args.include_organization_members if args.include_organization_members else False
    output_path = args.output_path if args.output_path else None
    threads_limit = int(args.threads_limit) if args.threads_limit else 5
    authentication = args.authentication if args.authentication else None
    include_authenticated_repos = args.include_authenticated_repos if args.include_authenticated_repos else False

    if not args.output_path:
        print("Error: The output path is not specified.")
        print("\nExiting...")
        exit(1)

    if not (args.users or args.organizations):
        print("Error: Both Github users and Github organizations are not specified.")
        print("\nExiting...")
        exit(1)

    if str.isdigit(str(threads_limit)) is False:
        print("Error: Specified threads specified is invalid.")
        print("\nExiting...")
        exit(1)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    if authentication is not None:
        if getReposURLs().checkAuthencation(authentication.split(":")[0], authentication.split(":")[1]) is False:
            print("Error: authentication failed.")
            print("\nExiting...")
            exit(1)
        else:
            username = authentication.split(":")[0]
            token = authentication.split(":")[1]
    else:
        username = None
        token = None

    if (include_authenticated_repos is True) and (authentication is None):
        print("Error: --include-authenticated-repos is used and --authentication is not provided.")
        print("\nExiting...")
        exit(1)

    URLs = []

    if include_authenticated_repos is True:
        URLs.extend(getReposURLs().fromAuthenticatedUser(username, token))

    if users is not None:
        users = users.replace(" ", "").split(",")
        for user in users:
            URLs.extend(getReposURLs().fromUser(user, username=username, token=token))

    if organizations is not None:
        organizations = organizations.replace(" ", "").split(",")

        for organization in organizations:
            if include_organization_members is False:
                URLs.extend(getReposURLs().fromOrg(organization, username=username, token=token))
            else:
                URLs.extend(getReposURLs().fromOrgIncludeUsers(organization, username=username, token=token))

    URLs = list(set(URLs))

    cloneBulkRepos(URLs, output_path, threads_limit=threads_limit, username=username, token=token)


if (__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
            print('\nKeyboardInterrupt Detected.')
            print('\nExiting...')
            exit(0)

# *** END *** #
