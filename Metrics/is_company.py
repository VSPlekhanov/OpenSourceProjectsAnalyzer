# MAIN IDEA:

# --------------------
# It is useful to know whether repository belongs to a company or not.
# If it does, we want to be able to say whether it is a big company.
# Moreover, Such metric might find its use in other metrics analysis.
# --------------------

# REALISATION DETAILS:
# --------------------
# Firstly, check whether repo owner is a github organization.
# After that we try to ping a website specified in organization profile.
# If website is alive - more probably this organization belongs to some company.

# Know we want to know if this is a big company.
# Big companies tend to have wiki page. So we use Wiki API to search for
# a company by name specified in github organization page.
# After that we are searching for foundation date in wiki page.
# If every step is successful - repo most probably belongs to a big company.
# --------------------


import os
import requests

from bs4 import BeautifulSoup
from github import Github

WIKI_SEARCH_API_URL = 'https://en.wikipedia.org/w/api.php?action=query&' \
                      'list=search&srsearch={}&utf8&format=json'
WIKI_GET_PAGE_URL = 'https://en.wikipedia.org/w/api.php?action=parse&' \
                    'prop=text&page={}&format=json'

COMPANY_ANSWER = '{} repository belongs to a company.'
BIG_COMPANY_ANSWER = '{} repository belongs to a big company.'
NOT_COMPANY_ANSWER = '{} repository does not belong to company.'


def determine_big_company(organization) -> bool:
    search_response = requests.get(
        WIKI_SEARCH_API_URL.format(organization.name))
    if search_response.status_code != 200:
        raise RuntimeError('Could not perform wiki search')
    wiki_page_name = search_response.json()['query']['search'][0]['title']

    page_response = requests.get(WIKI_GET_PAGE_URL.format(wiki_page_name))
    if page_response.status_code != 200:
        raise RuntimeError('Could not get wiki page')
    wiki_page = page_response.json()['parse']['text']['*']

    soup = BeautifulSoup(wiki_page, "html.parser")
    tags = soup.findAll('th', {'class': 'infobox-label'})
    founded_tag = list(filter(lambda x: x.getText() == 'Founded', tags))
    return True if founded_tag else False


def get_info(username, repo) -> str:
    pygithub = Github(os.getenv("GITHUB_API_TOKEN"))
    user = pygithub.get_user(username)
    if user.type != 'Organization':
        return NOT_COMPANY_ANSWER.format(repo)
    organization = pygithub.get_organization(username)
    if organization.blog is None:
        return NOT_COMPANY_ANSWER.format(repo)

    status_code = requests.get(organization.blog).status_code
    if 500 <= status_code <= 526:
        return NOT_COMPANY_ANSWER.format(repo)

    if determine_big_company(organization):
        return BIG_COMPANY_ANSWER.format(repo)

    return COMPANY_ANSWER.format(repo)
