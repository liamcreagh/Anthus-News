from collections import defaultdict
import pickle
from random import shuffle
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from urllib.request import urlopen
from PIL import Image
from io import BytesIO
import datetime
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q
import requests

__author__ = 'James'

from bs4 import BeautifulSoup
import feedparser
from content_acquisition.models import FeedRec
from articles.models import ArticleRec
from content_acquisition.ArticleWrapper import ArticleWrapper
from newspaper import Article, ArticleException
from parsers.string_parser import StringParser

clf = pickle.load(open('./pipe.p', 'rb'))
parser = StringParser()


from django import setup

setup()
val = URLValidator()


def aggregate():
    ArticleRec.objects.filter(article_published__lte= datetime.datetime.today()-datetime.timedelta(days=7)).delete()

    for f in shuffle(FeedRec.objects.all()):

        u = f.feed_url

        print(u)
        article_list = grab_rss(f)

        x = 0

        for a in article_list:
            x += 1
            print("Checking article: " + str(x))

            article = Article(url=a.url)

            try:
                article.build()
            except (ArticleException, UnicodeDecodeError, ValueError):
                print("Error: ArticleException")
                continue

            a.content = parser.parse(article.text)['text']
            print(len(a.content))
            if len(a.content) < 50:
                print("Error: Too short")
                continue

            a.tag = clf.predict([article.text])[0]

            width, height = get_image_size(article.top_image)

            if width > 100 or height > 100:
                a.img = article.top_image
            add_article(a)



def grab_rss(f):
    articles = defaultdict()
    url = f.feed_url
    etag = f.feed_etag
    modified = f.feed_modified

    feed = feedparser.parse(url, etag=f.feed_etag)

    if feed.status == 304:
        print("Not updated")
    else:
        try:
            f.feed_etag = feed['etag']
            f.save(update_fields=['feed_etag'])
        except KeyError:
            print("Error: No etag")
            try:
                f.feed_modified = feed['modified']
                f.save(update_fields=['feed_modified'])
            except KeyError:
                print("Error: No modified time")
                pass

        for entry in feed.entries:
            article_url = strip_params(entry.link)
            certain_article = ArticleRec.objects.filter(Q(article_title=entry.title) | Q(article_url=article_url))
            if certain_article.exists():
                certain_article.delete()
            if 'summary_detail' in entry:
                try:
                    summary = BeautifulSoup(entry.summary_detail.value)
                    summary = ' '.join(list(map(lambda x: x.text, summary('p')[:5])))
                except TypeError:
                    pass
                    summary = ''
            else:
                summary = ''
            try:
                time = entry['updated_parsed']
            except KeyError:
                try:
                    time = entry['published_parsed']
                except KeyError:
                    print("Error: No time")
                    continue

            if time is None:
                continue

            a = ArticleWrapper(entry.title, article_url, summary, feed.feed.link, time)

            articles[entry] = a

    print(str(len(articles)) + " new articles found.")

    return list(articles.values())


def add_article(a):

    a_rec = ArticleRec(article_url=a.url,
                       article_title=a.title,
                       article_description=a.description,
                       article_source=a.source,
                       article_published=a.time,
                       article_tag=a.tag,
                       article_image=a.img)
    print("Adding article:" + str(a_rec.article_id))
    a_rec.save()


    #
    # for w in a.content:
    #
    #     wf_rec = WordFrequencyRec(frequency=1)
    #     if WordRec.objects.filter(word=w).exists():
    #         wf_rec.word = WordRec.objects.get(word=w)
    #
    #     else:
    #         w_rec = WordRec(word=w)
    #         w_rec.save()
    #         wf_rec.word = w_rec
    #
    #     wf_rec.article = a_rec
    #     wf_rec.save()


def get_image_size(url):
    try:
        val(url)
        data = requests.get(url).content
        im = Image.open(BytesIO(data))

    except (ValidationError, IOError):
        return 0, 0
    else:
        return im.size


def strip_params(url):
    u = urlparse(url)[0:3]+('', '', '')
    return urlunparse(u)


aggregate()