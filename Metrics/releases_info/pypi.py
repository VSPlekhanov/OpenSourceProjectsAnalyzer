import requests
import datetime

from github import Repository
from bs4 import BeautifulSoup

from calc_stat import calc_stat


def get_release_date(tag):
    return datetime.datetime.strptime(
        tag.findAll('time')[0]['datetime'], '%Y-%m-%dT%H:%M:%S%z'
    ).replace(tzinfo=None)


def filter_pre_release(tag):
    return not tag.findAll(
        'span',
        {'class': 'badge badge--warning release__version-badge'}
    )


def get_pip_releases(repo: Repository):
    history_response = requests.get(
        f'https://pypi.org/project/{repo.name}/#history')
    if history_response.status_code != 200:
        raise RuntimeError(f'could not fetch history data for repo {repo.name}')

    soup = BeautifulSoup(history_response.content, "html.parser")
    tags = list(filter(
        filter_pre_release, soup.findAll('div', {'class': "release"})
    ))

    v_timestamps = [get_release_date(tag) for tag in tags]
    return calc_stat(v_timestamps, 'PIP')
