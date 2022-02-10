import os
from datetime import datetime
from github import Github


def prev_month(now):
    if now.month != 1:
        return now.replace(month=now.month - 1)
    return now.replace(year=now.year - 1, month=12)


def get_info(username, repo):
    now = datetime.now()
    one_year_ago = now.replace(year=now.year - 1)
    access_token = os.getenv("GITHUB_API_TOKEN")
    g = Github(access_token)
    repo = g.get_repo(f'{username}/{repo}')
    av_commits_count = int(repo.get_commits(since=one_year_ago).totalCount / 12)
    last_month = repo.get_commits(since=prev_month(now)).totalCount

    return f'Average commits count per month in last year: {av_commits_count}\n' \
           f'Commits count in the last month: {last_month}'