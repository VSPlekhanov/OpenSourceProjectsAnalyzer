from datetime import datetime, timedelta
from github import Github


def run(username, repo):
    keys_file = open("src/main/resources/python/Resources/access_token.txt")
    lines = keys_file.readlines()
    access_token = lines[0].rstrip()
    g = Github(access_token)
    repo = g.get_repo(f'{username}/{repo}')

    one_month_ago = datetime.now() - timedelta(days=30)
    issues = repo.get_issues(state='open', since=one_month_ago)
    total = repo.get_issues(state='all', since=one_month_ago).totalCount
    print(f'Total {total} issues created in last 30 days. {issues.totalCount} of them are open')
    i, count = 0, 0
    page = issues.get_page(i)
    while len(page) != 0:
        for issue in page:
            if issue.comments == 0:
                count += 1
        i += 1
        page = issues.get_page(i)

    return f'Open issues without comments: {count}\n' \
           f'Which is about {int(count * 100 / total)}% of all issues in last 30 days'
