#!/usr/bin/env python3
# coding=utf-8
# *******************************************************************
# *** GithubCloner ***
# * Description:
#   A script that clones public Github repositories
#   of users and organizations automatically.
# * Version:
#   v0.3
# * Homepage:
#   https://github.com/mazen160/GithubCloner
# * Author:
#   Mazin Ahmed <Mazin AT MazinAhmed DOT net>
# *******************************************************************

# Modules
import json
import os
try:
    import queue
except ImportError:
    import Queue as queue
import threading
import time

import argparse
import git
import requests
from sys import exit


class getReposURLs:
    def __init__(self, api_prefix, exclude_repos=None):
        self.user_agent = "GithubCloner (https://github.com/mazen160/GithubCloner)"
        self.headers = {'User-Agent': self.user_agent, 'Accept': '*/*'}
        self.timeout = 30
        self.api_prefix = api_prefix
        self.excluded_repos_list = [] if exclude_repos is None else\
            exclude_repos.strip().split(',')

    def filter_excluded_repos(self, url):
        '''
        True only if the url doesn't contain any string from
        `self.excluded_repos_list`
        '''
        return not any((excluded_repo in url
                        for excluded_repo in self.excluded_repos_list))

    def append_response(self, URLs, resp, key):
        '''Append the urls from response from a given criteria'''
        for i, _ in enumerate(resp):
            resp_i_key = resp[i][key]
            if self.filter_excluded_repos(resp_i_key):
                URLs.append(resp_i_key)

    def UserGists(self, user, username=None, token=None):
        """
        Returns a list of GIT URLs for accessible gists.
        Input:-
        user: Github user.
        Optional Input:-
        username: Github username.
        token: Github token or password.
        Output:-
        a list of Github gist repositories URLs.
        """

        URLs = []
        resp = []
        current_page = 1
        while (len(resp) != 0 or current_page == 1):
            API = "{0}/users/{1}/gists?page={2}".format(
                self.api_prefix, user, current_page)
            if (username or token) is None:
                resp = requests.get(API, headers=self.headers,
                                    timeout=self.timeout).text
            else:
                resp = requests.get(
                    API, headers=self.headers,
                    timeout=self.timeout,
                    auth=(username, token)).text
            resp = json.loads(resp)

            if self.checkResponse(resp) != 0:
                return []

            self.append_response(URLs, resp, "git_pull_url")
            current_page += 1
        return URLs

    def AuthenticatedGists(self, username, token):
        """
        Returns a list of gists of an authenticated user.
        Input:-
        username: Github username.
        token: Github token or password.
        Output:-
        a list of Github gist repositories URLs.
        """

        URLs = []
        resp = []
        current_page = 1
        while (len(resp) != 0 or current_page == 1):
            API = "{0}/gists?page={1}".format(self.api_prefix, current_page)
            resp = requests.get(API,
                                headers=self.headers,
                                timeout=self.timeout,
                                auth=(username, token)).text
            resp = json.loads(resp)
            self.append_response(URLs, resp, "git_pull_url")
            current_page += 1

        return URLs

    def fromUser(self, user, username=None, token=None, include_gists=False):
        """
        Retrieves a list of repositories for a Github user.
        Input:-
        user: Github username.
        Optional Input:-
        username: Github username.
        token: Github token or password.
        Output:-
        a list of Github repositories URLs.
        """

        URLs = []
        resp = []
        current_page = 1
        while (len(resp) != 0 or current_page == 1):
            API = "{0}/users/{1}/repos?per_page=40000000&page={2}".format(
                self.api_prefix, user, current_page)

            if (username or token) is None:
                resp = requests.get(API, headers=self.headers,
                                    timeout=self.timeout).text
            else:
                resp = requests.get(
                    API,
                    headers=self.headers,
                    timeout=self.timeout,
                    auth=(username, token)).text
            resp = json.loads(resp)

            if self.checkResponse(resp) != 0:
                return []

            self.append_response(URLs, resp, "git_url")

            if include_gists is True:
                URLs.extend(self.UserGists(
                    user, username=username, token=token))
            current_page += 1
        return URLs

    def fromOrg(self, org_name, username=None, token=None):
        """
        Retrieves a list of repositories for a Github organization.
        Input:-
        org_name: Github organization name.
        Optional Input:-
        username: Github username.
        token: Github token or password.
        Output:-
        a list of Github repositories URLs.
        """

        URLs = []
        resp = []
        current_page = 1
        while (len(resp) != 0 or current_page == 1):
            API = "{0}/orgs/{1}/repos?per_page=40000000&page={2}".format(
                self.api_prefix, org_name, current_page)
            if (username or token) is None:
                resp = requests.get(API, headers=self.headers,
                                    timeout=self.timeout).text
            else:
                resp = requests.get(
                    API,
                    headers=self.headers,
                    timeout=self.timeout,
                    auth=(username, token)).text
            resp = json.loads(resp)

            if self.checkResponse(resp) != 0:
                return []

            self.append_response(URLs, resp, "git_url")
            current_page += 1
        return URLs

    def fromOrgIncludeUsers(self,
                            org_name,
                            username=None,
                            token=None,
                            include_gists=False):
        """
        Retrieves a list of repositories for a Github organization
        and repositories of the Github organization's members.
        Input:-
        org_name: Github organization name.
        Optional Input:-
        username: Github username.
        token: Github token or password.
        Output:-
        a list of Github repositories URLs.
        """

        URLs = []
        members = []
        resp = []
        current_page = 1
        URLs.extend(self.fromOrg(org_name, username=username, token=token))

        while (len(resp) != 0 or current_page == 1):
            API = "{0}/orgs/{1}/members?per_page=40000000&page={2}".format(
                self.api_prefix, org_name, current_page)
            if (username or token) is None:
                resp = requests.get(API,
                                    headers=self.headers,
                                    timeout=self.timeout).text
            else:
                resp = requests.get(API,
                                    headers=self.headers,
                                    timeout=self.timeout,
                                    auth=(username, token)).text
            resp = json.loads(resp)

            if self.checkResponse(resp) != 0:
                return []

            current_page += 1
            for i in range(len(resp)):
                members.append(resp[i]["login"])

        for member in members:
            URLs.extend(self.fromUser(member,
                                      username=username,
                                      token=token,
                                      include_gists=include_gists))

        return URLs

    def checkAuthentication(self, username, token):
        """
        Checks whether an authentication credentials are valid or not.
        Input:-
        username: Github username.
        token: Github token or password.
        Output:-
        True: if the authentication credentials are valid.
        False: if the authentication credentials are invalid.
        """

        API = "{0}/user".format(self.api_prefix)
        resp = requests.get(API,
                            auth=(username, token),
                            timeout=self.timeout,
                            headers=self.headers)
        return resp.status_code == 200

    def checkResponse(self, response):
        """
        Validates whether there an error in the response.
        """
        try:
            if "API rate limit exceeded" in response["message"]:
                print('[!] Error: Github API rate limit exceeded')
                return 1
        except TypeError:
            pass

        try:
            if (response["message"] == "Not Found"):
                return 2  # The organization does not exist
        except TypeError:
            pass

        return 0

    def fromAuthenticatedUser(self, username, token):
        """
        Retrieves a list of Github repositories than an authenticated user
        has access to.
        Input:-
        username: Github username.
        token: Github token or password.
        Output:-
        a list of Github repositories URLs.
        """
        URLs = []
        resp = []
        current_page = 1

        while (len(resp) != 0 or current_page == 1):
            API = "{0}/user/repos?per_page=40000000&type=all&page={1}".format(
                self.api_prefix, current_page)
            resp = requests.get(API,
                                headers=self.headers,
                                timeout=self.timeout,
                                auth=(username, token)).text
            resp = json.loads(resp)

            self.append_response(URLs, resp, "git_url")
            current_page += 1
        return URLs


def parseGitURL(URL, username=None, token=None):
    """
    This function parses the GIT URL.
    """

    URL = URL.replace("git://", "https://")
    if (username or token) is not None:
        URL = URL.replace(
            "https://", "https://{0}:{1}@".format(username, token))
    return URL


def get_repopath(repo_username, repo_name, prefix_mode):
    """
    Returns a string of the repo path.
    """
    if prefix_mode == "none":
        repopath = repo_name
    elif prefix_mode == "underscore":
        repopath = repo_username + "_" + repo_name
    elif prefix_mode == "directory":
        repopath = repo_username + "/" + repo_name
    return repopath


def cloneRepo(URL,
              cloningpath,
              username=None,
              token=None,
              prefix_mode="underscore"):
    """
    Clones a single GIT repository.
    Input:-
    URL: GIT repository URL.
    cloningPath: the directory that the repository will be cloned at.
    Optional Input:-
    username: Github username.
    token: Github token or password.
    """

    try:
        try:
            if not os.path.exists(cloningpath):
                os.mkdir(cloningpath)
            if prefix_mode == "directory":
                repo_username = URL.split("/")[-2]
                if not os.path.exists(cloningpath + "/" + repo_username):
                    os.mkdir(cloningpath + "/" + repo_username)
        except Exception:
            print("Error: There is an error in creating directories")

        URL = parseGitURL(URL, username=username, token=token)

        repo_username = URL.split("/")[-2]
        repo_name = URL.split("/")[-1]

        repopath = get_repopath(repo_username, repo_name, prefix_mode)

        if repopath.endswith(".git"):
            repopath = repopath[:-4]

        if '@' in repopath:
            repopath = repopath.replace(repopath[:repopath.index("@") + 1], "")

        fullpath = cloningpath + "/" + repopath
        with threading.Lock():
            print(fullpath)

        if os.path.exists(fullpath):
            git.Repo(fullpath).remote().pull()
        else:
            git.Repo.clone_from(URL, fullpath)
    except Exception as e:
        print(e)
        print("Error: There was an error in cloning [{}]".format(URL))


def cloneBulkRepos(URLs,
                   cloningPath,
                   threads_limit=5,
                   username=None,
                   token=None,
                   prefix_mode="underscore"):
    """
    Clones a bulk of GIT repositories.
    Input:-
    URLs: A list of GIT repository URLs.
    cloningPath: the directory that the repository will be cloned at.
    Optional Input:-
    threads_limit: The limit of working threads.
    username: Github username.
    token: Github token or password.
    """

    Q = queue.Queue()
    threads_state = []
    for URL in URLs:
        Q.put(URL)
    while Q.empty() is False:
        if threading.active_count() < (threads_limit + 1):
            t = threading.Thread(target=cloneRepo, args=(Q.get(), cloningPath,),
                                 kwargs={"username": username,
                                         "token": token,
                                         "prefix_mode": prefix_mode})
            t.daemon = True
            t.start()
        else:
            time.sleep(0.5)

            threads_state.append(t)
    for _ in threads_state:
        _.join()


def main():
    """
    The main function.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user",
                        dest="users",
                        help="Github user (comma-separated input for multiple Github users).",
                        action='store')
    parser.add_argument("-org", "--org",
                        dest="organizations",
                        help="Github organization" +
                        "(comma-separated input for multiple Github organizations).",
                        action='store')
    parser.add_argument("--include-org-members",
                        dest="include_organization_members",
                        help="Include the members of a Github organization.",
                        action='store_true')
    parser.add_argument("-o", "--output-path",
                        dest="output_path",
                        help="The directory to use in cloning Git repositories.",
                        action='store')
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
    parser.add_argument("--include-gists",
                        dest="include_gists",
                        help="Include gists.",
                        action='store_true')
    parser.add_argument("--echo-urls",
                        dest="echo_urls",
                        help="Print gathered URLs only and then exit.",
                        action='store_true')
    parser.add_argument("--prefix-mode",
                        dest="prefix_mode",
                        help="Sets the prefix mode for the repo directory. "
                        "underscore: /Netflix_repo-name, directory:"
                        " /Netflix/repo-name, none: /repo-name",
                        action='store',
                        default="underscore")
    parser.add_argument("--api-prefix",
                        dest="api_prefix",
                        help="Github Enterprise domain to prefix to API calls",
                        action='store',
                        default="https://api.github.com")
    parser.add_argument("--exclude_repos",
                        dest="exclude_repos",
                        help="Exclude a list of comma separated repos: 'repo1,repo2,...'",
                        action="store")
    args = parser.parse_args()

    users = args.users if args.users else None
    organizations = args.organizations if args.organizations else None
    include_organization_members = args.include_organization_members\
        if args.include_organization_members else False
    output_path = args.output_path if args.output_path else None
    threads_limit = int(args.threads_limit) if args.threads_limit else 5
    authentication = args.authentication if args.authentication else None
    include_authenticated_repos = args.include_authenticated_repos\
        if args.include_authenticated_repos else False
    include_gists = args.include_gists if args.include_gists else False
    echo_urls = args.echo_urls if args.echo_urls else False
    prefix_mode = args.prefix_mode
    api_prefix = args.api_prefix
    exclude_repos = args.exclude_repos if args.exclude_repos else None

    if threads_limit > 10:
        print("Error: Using more than 10 threads may cause errors."
              "\nDecrease the amount of used threads.")
        print("\nExiting....")
        exit(1)

    if (not args.output_path) and (not echo_urls):
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

    if not echo_urls:
        try:
            if not os.path.exists(output_path):
                os.mkdir(output_path)
        except Exception as error:
            print("Error: There is an error creating output directory.")
            print(repr(error))
            exit(1)

    if authentication is not None:
        if ':' not in authentication:
            print('[!] Error: Incorrect authentication value, must be:'
                  ' <username>:<password_or_personal_access_token>')
            print('\nExiting...')
            exit(1)
        if getReposURLs(api_prefix,
                        exclude_repos).checkAuthentication(
                            authentication.split(":")[0],
                            authentication.split(":")[1]) is False:
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

    if prefix_mode not in ["none", "underscore", "directory"]:
        print("Error: prefix_mode must be one of: \"none\", \"underscore\", \"directory\".")
        print("\nExiting...")
        exit(1)

    URLs = []

    if include_authenticated_repos is True:
        URLs.extend(getReposURLs(
            api_prefix, exclude_repos).fromAuthenticatedUser(username, token))
        if include_gists is True:
            URLs.extend(getReposURLs(
                api_prefix, exclude_repos).AuthenticatedGists(username, token))

    if users is not None:
        users = users.replace(" ", "").split(",")
        for user in users:
            URLs.extend(getReposURLs(api_prefix, exclude_repos).fromUser(
                user,
                username=username,
                token=token,
                include_gists=include_gists))

    if organizations is not None:
        organizations = organizations.replace(" ", "").split(",")

        for organization in organizations:
            if include_organization_members is False:
                URLs.extend(getReposURLs(api_prefix, exclude_repos).fromOrg(
                    organization,
                    username=username,
                    token=token))
            else:
                URLs.extend(getReposURLs(api_prefix,
                                         exclude_repos).fromOrgIncludeUsers(
                    organization,
                    username=username,
                    token=token,
                    include_gists=include_gists))

    URLs = list(set(URLs))
    if echo_urls is True:
        for URL in URLs:
            print(parseGitURL(URL, username=username, token=token))
        return

    cloneBulkRepos(URLs, output_path, threads_limit=threads_limit,
                   username=username, token=token, prefix_mode=prefix_mode)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt Detected.')
        print('\nExiting...')
        exit(0)
