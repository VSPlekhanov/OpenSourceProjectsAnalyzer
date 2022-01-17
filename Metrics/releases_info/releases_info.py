# --------------------
# Track how often project releases are made.
# We are collecting info from github as well as
# PIP and Maven Central Repository
# --------------------


import os

from github import Github, Repository

from Metrics.common import get_project_language
from pypi import get_pip_releases
from maven_central import get_maven_central_releases
from calc_stat import calc_stat


def get_github_release_history(repo: Repository):
    releases = repo.get_releases()
    if not releases:
        return None
    v_timestamps = [r.published_at for r in releases]
    return calc_stat(v_timestamps, 'GitHub Releases')


def get_info(username, repo):
    g = Github(os.getenv("GITHUB_API_TOKEN"))
    repo = g.get_repo(f'{username}/{repo}')
    result = []

    git_data = get_github_release_history(repo)
    if git_data:
        result.append(git_data)

    language = get_project_language(repo)
    package_manager_data = None
    if language == 'Python':
        package_manager_data = get_pip_releases(repo)
    elif language == 'Java' or language == 'Kotlin':
        package_manager_data = get_maven_central_releases(repo)
    if package_manager_data:
        result.append(package_manager_data)
    return '\n\n'.join(result)


if __name__ == "__main__":
    get_info('danielgabitov', 'hse-2021-design')
