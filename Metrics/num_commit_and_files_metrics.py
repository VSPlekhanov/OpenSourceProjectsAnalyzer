"""
Description:

The project where the commit frequency past year
is high is likely to be maintained. Also we need to know whether
each commit affects a lot of files or not, since it can be useful - if there
are less commits but a lot of files changed on average in a big project, we can
conclude that this project is still active.
"""

from pydriller import Repository
from git import Repo, GitCommandError
from datetime import datetime, timedelta
from github import Github, RateLimitExceededException
import pytz

import os
import numpy as np


def count_total_commits(username, repo):
    url = f'https://github.com/{username}/{repo}'

    today = datetime.today()
    last_month = today - timedelta(days=365)
    last_month = last_month.replace(tzinfo=pytz.utc)
    try:

        count_commit = 0
        files_affected_by_commits = []

        for commit in Repository(f'https://github.com/{username}/{repo}', order='reverse').traverse_commits():

            commit_date = commit.committer_date
            commit_date = commit_date.replace(tzinfo=pytz.utc)

            if commit_date >= last_month:

                count_commit += 1
                files_current_commit = 0

                for file in commit.modified_files:
                    files_current_commit += 1

                files_affected_by_commits.append(files_current_commit)

        if files_affected_by_commits:
            median_files = int(np.median(files_affected_by_commits))
        else:
            median_files = 0

        output_string_commit = f'Total number of commits past 365 days: {count_commit}.'
        output_string_files = f'Median number of files changed in commit: {median_files}.'


        return print("\n".join([output_string_commit, output_string_files]))

    except GitCommandError:
        return print(f'Wrong URL of the OpenSource project...')

    except RateLimitExceededException:
        return print('Unfortunately, API access rate limit is exceeded...')
