"""
Description:

It is necessary to track frequency of pull requests past month in a project.
Apparently, if we consider the amount of closed pull requests among all, then
this metric will be more reliable.
"""

from datetime import datetime, timedelta
from github import Github, UnknownObjectException, RateLimitExceededException

import os


def get_info_pull_requests(username, repo):
    api_token = os.getenv('GITHUB_API_TOKEN')
    g = Github(api_token)
    try:
        repo = g.get_repo(f'{username}/{repo}')

        date = datetime.today()
        period = date - timedelta(days=30)

        issues = repo.get_issues(state='all', since=period, sort='Newest')
        closed_prs = 0
        total_prs = 0

        for issue in issues:
            if issue.pull_request:
                total_prs += 1

                if issue.state == 'closed':
                    closed_prs += 1
        if total_prs == 0:
            percentage_closed = 0
        else:
            percentage_closed = int(closed_prs / total_prs * 100)
        output_total = f'Total number of pull requests past 30 days: {total_prs}.'
        output_percentage = f'Amount of closed pull_requests is {percentage_closed} %.'

        return print('\n'.join([output_total, output_percentage]))

    except UnknownObjectException:
        return print(f'Wrong URL of the OpenSource project...')

    except RateLimitExceededException:
        return print('Unfortunately, API access rate limit is exceeded...')
