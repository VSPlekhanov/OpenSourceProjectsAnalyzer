import re
import requests
import typing
from datetime import datetime

from github import Repository

import Metrics.common
from calc_stat import calc_stat


MVN_SEARCH_URL = 'https://search.maven.org/solrsearch/select?' \
                 'wt=json&rows={rows}&page={page}&core=gav&' \
                 'q=g:{group_id} AND a:{artifact_id}'

MVN_SEARCH_ART_ID_URL = 'https://search.maven.org/solrsearch/select?' \
                        'q={group_id}&rows={rows}&page={page}&wt=json'

group_id_regex = re.compile(
    r'^\s*group(| )=(| )(\'[a-zA-Z.]+\'|"[a-zA-Z.]+")\s*$'
)


def fetch_all_versions(*, group_id: str, artifact_id: str):
    request_args = {'rows': 20, 'page': 0,
                    'group_id': group_id, 'artifact_id': artifact_id}
    total_releases_number: typing.Optional[int] = None
    releases_number = 0
    release_timestamps = []
    while not total_releases_number or releases_number < total_releases_number:
        response = requests.get(MVN_SEARCH_URL.format(**request_args))
        if response.status_code != 200:
            raise RuntimeError('could not fetch versions data from mvn search')
        response_json = response.json()['response']
        total_releases_number = response_json['numFound']
        releases_number += len(response_json['docs'])
        for elem in response_json['docs']:
            r_time = datetime.fromtimestamp(elem['timestamp'] / 1000)
            release_timestamps.append(r_time)
        request_args['page'] += 1
    return release_timestamps


def select_best_artifact_id(group_id: str) -> str:
    request_args = {'rows': 20, 'page': 0, 'group_id': group_id}
    total_artifacts_number: typing.Optional[int] = None
    artifacts_number = 0
    artifacts = {}
    while not total_artifacts_number or artifacts_number < total_artifacts_number:
        response = requests.get(MVN_SEARCH_ART_ID_URL.format(**request_args))
        if response.status_code != 200:
            raise RuntimeError('could not fetch versions data from mvn search')
        response_json = response.json()['response']
        total_artifacts_number = response_json['numFound']
        artifacts_number += len(response_json['docs'])
        for elem in response_json['docs']:
            artifacts[elem['a']] = elem['versionCount']
        request_args['page'] += 1
    return max(artifacts, key=artifacts.get)


def get_maven_central_releases(repo: Repository):
    last_commit = repo.get_commit(repo.default_branch)
    build_tool = common.get_build_tool(last_commit.commit.tree)
    if build_tool == common.BuildTool.maven:
        group_id, artifact_id = common.retrieve_pom_project_info(repo)
        v_timestamps = fetch_all_versions(
            group_id=group_id, artifact_id=artifact_id)
        if not v_timestamps:
            return f'There is no artifact <{artifact_id}> with group ' \
                   f'<{group_id}> in maven central repository'
        return calc_stat(v_timestamps, 'Maven Central')
    elif build_tool == common.BuildTool.gradle:
        group_id = common.retrieve_gradle_project_info(repo)
        artifact_id = select_best_artifact_id(group_id=group_id)
        v_timestamps = fetch_all_versions(
            group_id=group_id, artifact_id=artifact_id)
        if not v_timestamps:
            return f'There is no artifacts with group ' \
                   f'<{group_id}> in maven central repository'
        return calc_stat(v_timestamps, source='Maven Central')
