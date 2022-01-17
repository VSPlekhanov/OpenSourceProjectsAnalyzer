# --------------------
# In developing projects, functionality is being added. As a rule,
# such functionality should be tested. Hence the idea for the metric:
# estimate the number of commits in which tests were changed or added.
# --------------------


import os
import datetime

from github import Github

UNTIL = datetime.datetime.now() - datetime.timedelta(days=365)
MAX_COMMIT = 100


def get_info(username, repo):
    g = Github(os.getenv("GITHUB_API_TOKEN"))
    repo = g.get_repo(f'{username}/{repo}')
    commits = repo.get_commits(since=UNTIL)
    good_commits_amount = 0
    for i, commit in enumerate(commits):
        if i >= MAX_COMMIT:
            break
        for file in commit.files:
            if 'test' in file.filename.lower():
                good_commits_amount += 1
                break
    return f'Number of commits where tests have been changed: {good_commits_amount}'
