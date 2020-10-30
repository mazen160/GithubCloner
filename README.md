GithubCloner
=============

# A script that clones Github repositories of users and organizations. #


# Usage #

| Description                                               | Command                                                                     |
|-----------------------------------------------------------|-----------------------------------------------------------------------------|
| Help                                                      | `./githubcloner.py --help`                                                  |
| Clone all repositories of a single user.                  | `./githubcloner.py --user user -o /tmp/output`                              |
| Clone all repositories of multiple users.                 | `./githubcloner.py --user user1,user2,user3 -o /tmp/output`                 |
| Clone all repositories of a single organization.          | `./githubcloner.py --org organization -o /tmp/output`                       |
| Clone all repositories of multiple organizations.         | `./githubcloner.py --org organization1,organization2 -o /tmp/output`        |
| Clone all repositories of an organization in a hosted Github       | `./githubcloner.py --org organization -o /tmp/output` --api-prefix https://git.company.com/api/v3       |
| Modify the amount of used threads                         | `./githubcloner.py --user user --threads 10 -o /tmp/output`                 |
| Clone all repositories of an organization, along with all repositories of the organization's members.       | `./githubcloner.py --org organization --include-org-members -o /tmp/output` |
| Use Github authentication in the task.                    | `./githubcloner.py --org organization -o /tmp/output --authentication user:token`|
| Clone authenticated repositories that the authenticated user has access to. | `./githubcloner.py -o /tmp/output --authentication user:token --include-authenticated-repos`|
| Include gists.                                            | `./githubcloner.py --user user -o /tmp/output --include-gists`              |
| Save repos as username_reponame                           | `./githubcloner.py --user user -o /tmp/output --prefix-mode underscore`     |
| Save repos as username/reponame                           | `./githubcloner.py --user user -o /tmp/output --prefix-mode directory`      |
| Save repos as reponame                                    | `./githubcloner.py --user user -o /tmp/output --prefix-mode none`           |
| Exclude comma separated list of repos                     | `./githubcloner.py --user user -- exclude_repos repo1,repo2,repo3,...`      |
| Print gathered URLs only and then exit.                   | `./githubcloner.py --user user --include-gists --echo-urls`                 |


# Compatibility #
The project is compatible with both Python 2 and Python 3.


# Requirements #
* Python2 or Python3
* requests
* gitpython


# Testing
* nosetests -vx


# License #
The project is licensed under MIT License.

# Legal Disclaimer #
This project is made for educational and ethical testing purposes only. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program.


# Author #
## *Mazin Ahmed* ##
* Website: [https://mazinahmed.net](https://mazinahmed.net)
* Email: *mazin AT mazinahmed DOT net*
* Twitter: [https://twitter.com/mazen160](https://twitter.com/mazen160)
* Linkedin: [http://linkedin.com/in/infosecmazinahmed](http://linkedin.com/in/infosecmazinahmed)

# Update from qkzk

* option to exclude a bunch of repos
* refactor
