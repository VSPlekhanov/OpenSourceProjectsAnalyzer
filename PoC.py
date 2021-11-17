{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 64,
   "id": "b3fe5787",
   "metadata": {},
   "outputs": [],
   "source": [
    "import datetime\n",
    "import requests\n",
    "import re\n",
    "import matplotlib.pyplot as plt"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "bbe14e00",
   "metadata": {},
   "source": [
    "## Core Idea\n",
    "\n",
    "In developing projects, functionality is being added. As a rule, such functionality should be tested.\n",
    "\n",
    "Hence the idea for the metric: we estimate the number of commits over the past year in which tests were\n",
    "changed/added.\n",
    "\n",
    "We are not considering all commits, but only those in which there were changes in the project source files (*.py files)\n",
    "\n",
    "A commit is considered to be 'good' if it contains changes in test_\\*.py files\n",
    "\n",
    "There can be many commits per year, so no more than N commits are counted\n",
    "\n",
    "Metrics output: |good_commits| / |N|"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 65,
   "id": "769f54ab",
   "metadata": {},
   "outputs": [],
   "source": [
    "input_data = [\n",
    "'https://github.com/PyCQA/pylint | 10',\n",
    "'https://github.com/PyCQA/flake8 | 10',\n",
    "'https://github.com/deepfakes/faceswap | 9',\n",
    "'https://github.com/cookiecutter/cookiecutter | 8',\n",
    "'https://github.com/zappa/zappa | 7',\n",
    "'https://github.com/box/box-python-sdk | 7',\n",
    "'https://github.com/box/flaky | 6',\n",
    "'https://github.com/zalando/python-nsenter | 6',\n",
    "'https://github.com/jazzband/django-pipeline | 5',\n",
    "'https://github.com/tiangolo/full-stack | 4',\n",
    "'https://github.com/miracle2k/flask-assets | 3',\n",
    "'https://github.com/tiangolo/docker-auto-labels | 2',\n",
    "'https://github.com/tiangolo/bitbucket_issues_to_redmine_csv | 1',\n",
    "'https://github.com/zalando-stups/senza | 1',\n",
    "'https://github.com/aizvorski/scikit-video | 1',\n",
    "]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 66,
   "id": "277a1aa2",
   "metadata": {},
   "outputs": [],
   "source": [
    "SECRET = ''\n",
    "## ^ PUT YOUR SECRET KEY HERE ^\n",
    "\n",
    "UNTIL = datetime.datetime(year=2020, month=11, day=1)\n",
    "COMMITS_AMOUNT = 50\n",
    "\n",
    "session = requests.Session()\n",
    "assert SECRET\n",
    "session.auth = ('DanielGabitov', SECRET)\n",
    "test_function_pattern = re.compile(r'^(test_.*\\.py|.*_test\\.py)$')\n",
    "source_file_pattern = re.compile(r'^.*py$')\n",
    "\n",
    "\n",
    "def evaluate_commit(commit_data, owner, repo):\n",
    "    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{commit_data[\"sha\"]}'\n",
    "    fetched_data = session.get(url).json()\n",
    "    file_names = [file['filename'].split('/')[-1] for file in fetched_data['files']]\n",
    "    file_names = list(set(file_names))\n",
    "    if all(not source_file_pattern.match(file_name) for file_name in file_names):\n",
    "        return None\n",
    "    if any(test_function_pattern.match(file_name) for file_name in file_names):\n",
    "        return True\n",
    "    return False\n",
    "\n",
    "\n",
    "def get_score(owner, repo):\n",
    "    good = 0\n",
    "    total = 0\n",
    "    page = 1\n",
    "    commit_amount = 0\n",
    "    commits = session.get(f\"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100&page={page}\").json()\n",
    "    flag = True\n",
    "    while flag:\n",
    "        for commit in commits:\n",
    "            commit_amount += 1\n",
    "            date: datetime = datetime.datetime.strptime(commit['commit']['committer']['date'], \"%Y-%m-%dT%H:%M:%SZ\")\n",
    "            if date < UNTIL:\n",
    "                flag = False\n",
    "                break\n",
    "            result = evaluate_commit(commit, owner, repo)\n",
    "            if result is None:\n",
    "                continue\n",
    "            if result:\n",
    "                good += 1\n",
    "            total += 1\n",
    "            if total >= COMMITS_AMOUNT:\n",
    "                flag = False\n",
    "        page += 1\n",
    "        commits = session.get(f\"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100&page={page}\").json()\n",
    "        if len(commits) == 0:\n",
    "            break\n",
    "    if total == 0:\n",
    "        return 0\n",
    "    return good / total\n",
    "\n",
    "\n",
    "def conduct_experiment(repos_data):\n",
    "    results = []\n",
    "    for line in repos_data:\n",
    "        repo, my_score = line.replace(' ', '').split('|')\n",
    "        x = repo.split('/')\n",
    "        owner = x[-2]\n",
    "        repo = x[-1]\n",
    "        score = get_score(owner, repo)\n",
    "        results.append((my_score, score))\n",
    "    return results"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 67,
   "id": "6f6ed675",
   "metadata": {},
   "outputs": [],
   "source": [
    "exp_results = conduct_experiment(input_data)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 68,
   "id": "dd92be41",
   "metadata": {},
   "outputs": [],
   "source": [
    "def print_plot():\n",
    "    y_labels_predicted = [int(x[0]) for x in exp_results]\n",
    "    for i in range(0, len(data)):\n",
    "        plt.plot(i, y_labels_predicted[i], 'go')\n",
    "\n",
    "    y_labels_actual = [x[1] for x in exp_results]\n",
    "    for i in range(0, len(data)):\n",
    "        plt.plot(i, y_labels_actual[i] * 10, 'yo')\n",
    "    plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "174f2846",
   "metadata": {},
   "source": [
    "## Results"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 70,
   "id": "c1afaef7",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "print_plot()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "a35e742a",
   "metadata": {},
   "source": [
    "Yellow marks - the results of the metric, green marks - my rating for projects on a scale from 1 to 10.\n",
    "\n",
    "\n",
    "Having tested the metric on the sample, we can conclude about the relationship between the 'alive' project and the result obtained.\n",
    "I would use the metric in the following scenario: if the metric output > X (for instance 0.10), then the project is most likely supported and 'alive'."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
