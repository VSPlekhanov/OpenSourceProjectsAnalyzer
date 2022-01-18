# --------------------
# A good open source project is used by many people.
# We want to evaluate how many other projects use our open source project.
# --------------------

# NOTE
# --------------------
# Example of usage count measured by github itself:
# https://github.com/projectlombok/lombok/network/dependents
# The problem:
# https://github.community/t/bug-project-not-showing-network-dependents/3161
# So if we have not found any dependents project, we are using github
# search API looking for build files where our project is mentioned
# --------------------


import os
import requests
from github import Github
from bs4 import BeautifulSoup

import common

SEARCH_URL = 'https://api.github.com/search/code?q={project} filename:{filename}'
DEPENDENTS_URL = 'https://github.com/{username}/{repo_name}/network/dependents'


def github_search_info(username, repo):
    g = Github(os.getenv("GITHUB_API_TOKEN"))
    repo = g.get_repo(f'{username}/{repo}')
    lang = common.get_project_language(repo)

    if lang == 'Python':
        filenames = ['requirements.txt']
        project_name = repo.name
    elif lang == 'Java' or lang == 'Kotlin':
        filenames = ['build.gradle', 'pom.xml']
        build_tool = common.get_build_tool(
            repo.get_git_tree(repo.default_branch))
        if build_tool == common.BuildTool.maven:
            group_id, _ = common.retrieve_pom_project_info(repo)
        elif build_tool == common.BuildTool.gradle:
            group_id = common.retrieve_gradle_project_info(repo)
        else:
            raise RuntimeError(f'build tool {build_tool.name} is not supported.\n'
                               f'List of supported tools: '
                               f'{common.SUPPORTED_BUILD_TOOLS}')
        project_name = group_id
    else:
        raise RuntimeError(f'not supported language: {lang}.\n'
                           f'List of supported languages: '
                           f'{common.SUPPORTED_LANGUAGES}')

    usages = 0
    headers = {'Authorization': 'token ' + os.getenv("GITHUB_API_TOKEN")}
    args = {'project': project_name}
    for i, file in enumerate(filenames):
        args['filename'] = file
        response = requests.get(SEARCH_URL.format(**args), headers=headers)
        if response.status_code != 200:
            return f'Could not get info form github search API. Probably secondary rate limit exceeded.'
        usages += response.json()['total_count']
    return f'Project usages number: {usages}'


def get_info(username, repo):
    response = requests.get(
        DEPENDENTS_URL.format(username=username, repo_name=repo))
    if response.status_code != 200:
        raise RuntimeError(f'could not fetch github dependents page. '
                           f'Error message: {response.text}')
    soup = BeautifulSoup(response.text, 'html.parser')
    tag = soup.findAll('a', {'class': 'btn-link selected'})[0]
    if not tag:
        raise RuntimeError('could not find dependents tag')
    usages = ''.join(filter(str.isdigit, tag.text))
    if usages == '0':
        return github_search_info(username, repo)
    return f'Project usages number: {usages}'
