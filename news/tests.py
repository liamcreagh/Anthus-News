import collections
from itertools import cycle, islice
from math import ceil
import operator
from pprint import pprint
from django.test import TestCase

# Create your tests here.
from articles.models import ArticleRec


def main_news():
    prefs = [(14, 50),
 (11, 21),
 (5, 20),
 (3, 18),
 (12, 18),
 (1, 17),
 (0, 16),
 (15, 15),
 (8, 8),
 (10, 7),
 (7, 6),
 (9, 5),
 (6, 3),
 (4, 2)]

    sum_prefs = sum([p[1] for p in prefs])
    maximum = max(prefs, key=operator.itemgetter(1))[1]
    N_articles = 200

    prefs = [(t, ceil(N_articles*v/sum_prefs)) for t, v in prefs]
    prefs = sorted(prefs, key=operator.itemgetter(1), reverse=True)

    pprint(prefs)

    pprint(sum([a[1] for a in prefs]))

    num_topics = len(prefs)

    articles = []

    for tag, value in prefs:
        news = ArticleRec.objects.with_string_topics(tag)[:int(value)]
        sz = ceil(float(len(news))/float(num_topics))
        n = [news[i:i+sz] for i in range(0, len(news), sz)]
        articles.append(n)

    chunked = []

    for i, articleset in enumerate(articles):

        for a in articles:
            try:
                chunked.append(a[i])
            except IndexError:
                pass

    ranked_articles = []
    from itertools import chain


    for c in chunked:
        ranked_articles.extend([a for a in list(chain.from_iterable(zip(c)))])

    pprint(len(ranked_articles))

main_news()
