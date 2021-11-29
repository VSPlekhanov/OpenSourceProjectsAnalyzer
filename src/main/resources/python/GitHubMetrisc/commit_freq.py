from datetime import datetime
from github import Github


def run(username, repo):
    now = datetime.now()
    one_year_ago = now.replace(year=now.year - 1)
    keys_file = open("src/main/resources/python/Resources/access_token.txt")
    lines = keys_file.readlines()
    access_token = lines[0].rstrip()
    g = Github(access_token)
    repo = g.get_repo(f'{username}/{repo}')
    av_commits_count = int(repo.get_commits(since=one_year_ago).totalCount / 12)
    last_month = repo.get_commits(since=now.replace(month=now.month - 1)).totalCount
    return f'Average commits count per month in last year: {av_commits_count}\n' \
           f'Commits count in the last month: {last_month}'