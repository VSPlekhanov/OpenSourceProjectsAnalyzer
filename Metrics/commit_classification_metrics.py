"""
Description:

In this metrics we try to distinguish light commit - that is documentary, comments and etc. and
significant commit - the one which affects source code. So we try to build simple model using Naive Bayes
approach to detect several languages (english, german, russian, italian) and if the language not english, it is
definitely a comment so if not we try to parse other string expression in order to detect code samples (some symbols
that are very likely for code in many programming languages). We parse last 100 commits line by line from Github and
classify each added line in every commit and then we can conclude approximate number of significant commits using
our simple model.
"""

from pydriller import Repository
from git import Repo, GitCommandError
from github import Github, RateLimitExceededException

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from datetime import datetime, timedelta
from collections import Counter

import sklearn.metrics
import numpy as np


class TextClassifyModel:

    def __init__(self):
        self.pipeline = None
        self.X = None
        self.y = None
        self.y_test = None
        self.X_test = None

    @staticmethod
    def text_preprocessing(path):
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()

            punctuation = ['?', '!', '...', '\n']

            for punc in punctuation:
                text = text.replace(punc, '.')

            stopsymbols = ['<<', '>>', '«', '»', ':', ';', "'",
                           '"', '  ', '/', '\\', 'I', '1', '2',
                           '3', '4', '5', '6', '7', '8', '9',
                           'V']

            for symbol in stopsymbols:
                text = text.replace(symbol, '')

            sentences = text.split('.')

            for i in range(len(sentences)):
                sentences[i] = sentences[i].strip()

            result = [i for i in sentences if i]

            return result

    def fit(self):

        russian = self.text_preprocessing('datasets/ru_words.txt')
        english = self.text_preprocessing('datasets/en_words.txt')
        italian = self.text_preprocessing('datasets/it_words.txt')
        german = self.text_preprocessing('datasets/ge_words.txt')

        self.X = np.array(italian + german + russian + english)

        self.y = np.array(
            ['italian'] * len(italian) + ['german'] * len(german) +
            ['russian'] * len(russian) + ['english'] * len(english))

        X_train, self.X_test, y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.25, random_state=1)

        freq_counter = CountVectorizer(analyzer='char', ngram_range=(2, 2))

        self.pipeline = Pipeline([
            ('vectorizer', freq_counter),
            ('model', MultinomialNB())
        ])

        self.pipeline.fit(X_train, y_train)

    def code_identify(self, data):

        code_samples = ['=', '/', '\\', '|', '%', '^',
                        '*', '+', ' !=', '{', '}', '_',
                        '&', '~', '@', '[', ']', '>', '<']

        output = self.pipeline.predict(np.array([data]))[0]

        if output != 'english':
            return output

        for ind, elem in enumerate(data):

            if elem == '.':
                if ind + 1 <= len(data) - 1 and not data[ind + 1].isupper() and data[ind + 1].isalpha():
                    output = 'code'

            if elem in code_samples:
                output = 'code'

            if elem.isupper() and ind != 0 and data[ind - 1] != '.':
                if data[ind - 1].isalpha() and data[ind - 1].islower():
                    output = 'code'

        return output


def get_info_commit_classification(username, repo):

    ClsModel = TextClassifyModel()

    ClsModel.fit()

    url = f'https://github.com/{username}/{repo}'

    i = 0

    predicted = []
    try:
        for commit in Repository(url, order='reverse').traverse_commits():

            i += 1
            for file in commit.modified_files:

                for added_lines in file.diff_parsed['added']:
                    predicted.append(ClsModel.code_identify(added_lines[1]))

            if i > 100:
                break

        c = Counter(predicted)

        result = round(c['code'] / sum(c.values()) * 100, 1)
        output_str = f'Approximate number of code source changing commits: {result} %.'

        return print(output_str)


    except GitCommandError:
        return print(f'Wrong URL of the OpenSource project...')

    except RateLimitExceededException:
        return print('Unfortunately, API access rate limit is exceeded...')
