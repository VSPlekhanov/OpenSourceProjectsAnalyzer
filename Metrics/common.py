import requests
import re
from enum import Enum

from github import Repository, Github, GitTree
from bs4 import BeautifulSoup

GIT_RAW_FILE_URL = 'https://raw.githubusercontent.com/{owner}/' \
                   '{repo}/{branch}/{file_path}'

group_id_regex = re.compile(
    r'^\s*group(| )=(| )(\'[a-zA-Z.]+\'|"[a-zA-Z.]+")\s*$'
)


class BuildTool(Enum):
    maven = 0
    gradle = 1


SUPPORTED_BUILD_TOOLS = [tool.name for tool in BuildTool]


class Context:
    def __init__(self, *, github: Github, repo: Repository, language: str, build_tool: BuildTool):
        self.github = github
        self.repo = repo
        self.language = language
        self.build_tool = build_tool
    

def get_raw_file(*, owner: str, repo_name: str, branch: str, file_path: str):
    response = requests.get(GIT_RAW_FILE_URL.format(
        owner=owner, repo=repo_name, branch=branch, file_path=file_path))
    if response.status_code != 200:
        raise RuntimeError(f'could not fetch raw file {file_path} '
                           f'from {owner}/{repo_name}/{branch}')
    return response.text


def get_build_tool(tree: GitTree):
    build_tools = []
    for elem in tree.tree:
        filename = elem.path
        if filename == 'pom.xml':
            build_tools.append(BuildTool.maven)
        elif filename == 'gradlew':
            build_tools.append(BuildTool.gradle)

    if len(build_tools) < 1:
        raise RuntimeError(f'could not determine build tool. List of supported build tools: \n'
                           f'{SUPPORTED_BUILD_TOOLS}\n')

    if len(build_tools) > 1:
        raise RuntimeError(f'ambiguous build tools: {build_tools}')

    return build_tools[0]


def retrieve_gradle_project_info(repo: Repository):
    tree = repo.get_git_tree(repo.default_branch, recursive=True)
    build_files = []
    for elem in tree.tree:
        if elem.path.endswith('.gradle') or elem.path.endswith('.gradle.kts'):
            build_files.append(elem.path)
    for file in build_files:
        file_content = get_raw_file(
            owner=repo.owner.login, repo_name=repo.name,
            branch=repo.default_branch, file_path=file)
        for line in file_content.split('\n'):
            res = group_id_regex.match(line)
            if res:
                return res.group(3).replace('\'', '').replace('"', '')
    raise RuntimeError('could not determine groupId of gradle project')


def retrieve_pom_project_info(repo: Repository):
    pom_file = get_raw_file(owner=repo.owner.login, repo_name=repo.name,
                            branch=repo.default_branch, file_path='pom.xml')
    # todo add lxml to requirements
    soup = BeautifulSoup(pom_file, 'lxml')
    group_id = soup.project.groupid.text
    artifact_id = soup.project.artifactid.text
    if group_id is None or artifact_id is None:
        raise RuntimeError('could not determine group_id '
                           f'and artifact_id from pom.xml:\n {pom_file}')
    return group_id, artifact_id


SUPPORTED_LANGUAGES = {'Java', 'Kotlin', 'Python'}


def get_project_language(repo: Repository):
    repo_used_lang = repo.get_languages()
    lang_to_consider = {}
    for language in repo_used_lang:
        if language in SUPPORTED_LANGUAGES:
            lang_to_consider[language] = repo_used_lang[language]
    if not lang_to_consider:
        raise RuntimeError('Could not determine language.\n'
                           f'List of supported languages: {SUPPORTED_LANGUAGES}\n'
                           f'List of used languages in repository: '
                           f'{repo_used_lang.keys()}')
    max_code = max(lang_to_consider.values())
    best_lang = next(key for key in lang_to_consider.keys()
                     if lang_to_consider[key] == max_code)
    return best_lang
