# --------------------
# A good open source project is used by many people.
# We want to evaluate how many other projects use our open source project.
# In order to to so, we are using github search API looking for build files
# where our project is mentioned
# --------------------


import os
import requests
from dotenv import load_dotenv
from github import Github

import common

load_dotenv()

SEARCH_URL = 'https://api.github.com/search/code?q={project} filename:{filename}'


def get_info(username, repo):
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
