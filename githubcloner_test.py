import githubcloner


def test_get_repopath():
    assert githubcloner.get_repopath("user", "repo", "none") == "repo"
    assert githubcloner.get_repopath("user", "repo", "underscore") == "user_repo"
    assert githubcloner.get_repopath("user", "repo", "directory") == "user/repo"
