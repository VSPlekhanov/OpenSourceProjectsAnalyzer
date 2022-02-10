"""
Description:

It is definitely very essential to track if issues and pull
requests are resolved in a project. So we should consider
median time of resolution those in order to estimate an activity
of the contributors. Also if there are a lot of comments in pull
requests it means that the code is frequently reviewed.
"""

import os
import numpy as np

from datetime import datetime, timedelta
from github import Github, UnknownObjectException, RateLimitExceededException


def get_median_time_issue_and_pr(username, repo):
    api_token = os.getenv('GITHUB_API_TOKEN')
    g = Github(api_token)

    try:
        repo = g.get_repo(f'{username}/{repo}')

        today = datetime.today()
        last_month = today - timedelta(days=60)
        issues = repo.get_issues(state='all', since=last_month, sort='Newest')

        total_time_issues = []
        total_time_prs = []
        pull_request_comments = []
        issue_comments = []

        for issue in issues:

            if issue.created_at and issue.created_at >= last_month:

                if not issue.closed_at:
                    closed_at = today
                else:
                    closed_at = issue.closed_at
                time_issue = closed_at - issue.created_at

                if issue.pull_request:
                    pull_request_comments.append(issue.comments)
                    total_time_prs.append(time_issue.total_seconds() / (3600 * 24))
                else:
                    issue_comments.append(issue.comments)
                    total_time_issues.append(time_issue.total_seconds() / (3600 * 24))

        if total_time_issues:
            median_issues = (round(np.median(total_time_issues), 1))
        else:
            median_issues = 0.0

        if total_time_prs:
            median_prs = (round(np.median(total_time_prs), 1))
        else:
            median_prs = 0.0

        if pull_request_comments:
            median_comments_pr = (int(np.median(pull_request_comments)))
        else:
            median_comments_pr = 0


        output_issues = f'Median time of issue resolution past 2 months: {median_issues} days.'
        output_prs = f'Median time of pull request resolution past 2 months: {median_prs} days.'
        output_comments_pr = f'Median comments in pull_request: {median_comments_pr}.'

        return print("\n".join([output_issues, output_prs, output_comments_pr]))

    except UnknownObjectException:
        return print(f'Wrong URL of the OpenSource project...')

    except RateLimitExceededException:
        return print('Unfortunately, API access rate limit is exceeded...')
