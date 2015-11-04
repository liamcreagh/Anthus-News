from collections import Counter
from datetime import time, datetime
from itertools import chain, cycle, islice
from math import ceil
import operator
from pprint import pprint
import random
import collections
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import psycopg2
import sys
import sklearn
from sklearn.hmm import normalize
import tweepy
from articles.models import ArticleRec
from .forms import SignUpForm, LogInForm, GetTwitterURL
from user_profile.models import UserProfileRec

import logging

consumer_token = '0LA4gRkTxqKisEBBUia2n6ycc'
consumer_secret = 'WERUhw4tLvYVIDpCkB9hqE9ExBVOVhDDtVrSSwm1wO91mTHjpW'
callback_url = 'http://csi6220-2-vm4.ucd.ie/callback'

topics = ['art', 'business', 'celebrity', 'design', 'education', 'entertainment', 'fashion', 'film', 'food', 'health', 'music', 'politics', 'science', 'sport', 'tech', 'travel']
CSS_COLOR_NAMES = ["#C30CBB","#D65AD1","#CB31C4","#A3009C","#7E0078","#ED0F4E","#F3658E","#EF3A6E","#DD003F","#AA0031","#671CC5","#9865D8","#7D3FCC","#4F0AA6","#3D0880","Indigo"]
icons = ["fa fa-paint-brush", "fa fa-briefcase", "fa fa-users", "fa fa-pencil", "fa fa-graduation-cap", "fa fa-star", "fa fa-diamond", "fa fa-film", "fa fa-cutlery","fa fa-heartbeat","fa fa-music","fa fa-university","fa fa-flask","fa fa-futbol-o", "fa fa-laptop", "fa fa-plane"]

topic_tags = {t: {'name': name, 'icon': icons[t], 'colour': CSS_COLOR_NAMES[t]} for t, name in enumerate(topics)}

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

twitter_given = False

def index(request):
    title = "Home Page"
    user = request.user

    # url = "http://www.irishtimes.com/news/politics/misplaced-ibrc-minutes-confirm-siteserv-writedown-was-119-million-1.2237239"
    # response = urllib.request.urlopen(url)
    # html = response.read()
    # article_soup = BeautifulSoup(html)
    # article_text = article_soup.find('section', property='articleBody').get_text()
    # print(article_text)

    #article_text = "Filler "

    if request.user.is_authenticated():
        return my_news(request)
    else:
        return render(request, "landing.html", {})



def main_news(request, template='main_news.html', page_template='articles.html'):
    prefs = [(1, 35), (4, 25), (10, 50), (7, 100), (6, 10)]

    minimum = min(prefs, key=operator.itemgetter(1))[1]
    N_articles = 200

    prefs = [(t, N_articles*v/(5*minimum)) for t, v in prefs]

    prefs = sorted(prefs, key=operator.itemgetter(1), reverse=True)

    num_topics = len(prefs)

    articles = []

    for tag, value in prefs:
        news = ArticleRec.objects.with_string_topics(tag)[:int(value)]
        sz = ceil(float(len(news))/float(num_topics))
        n = [news[i:i+sz] for i in range(0, len(news), sz)]
        pprint([b.article_tag['name'] for a in n for b in a])
        articles.append(n)

    chunked = []

    for i, articleset in enumerate(articles):
        chunked.append([a[i] for a in articles])
    ranked_articles = []
    from itertools import chain


    for c in chunked:
        ranked_articles.extend([a for a in list(chain.from_iterable(zip(c)))])


    new_articles = []

    # for ar in articles:
    #     for a in ar:
    #         t = a.article_tag
    #         a.article_tag = {'name': topics[t].upper(), 'icon': icons[t], 'colour': CSS_COLOR_NAMES[t]}

    with_image = [(True, item) for item in ranked_articles if not (item.article_image is None or item.article_image is '')]
    no_image = [a for a in ranked_articles if a.article_image is "" or a.article_image is None]

    paired_no_image = [(False, item1, item2, item3) for item1, item2, item3 in list(zip(no_image[::3], no_image[1::3], no_image[2::3]))]

    article_list = list(map(next, random.sample([iter(with_image)]*len(with_image) + [iter(paired_no_image)]*len(paired_no_image),
                                len(with_image)+len(paired_no_image))))



    # article_list = paired_no_image
    context = {
        'entries': article_list,
        'topics': topics,
        'page_template': page_template,
    }

    if request.is_ajax():
        template = page_template

    return render_to_response(template,
                              context,
                              context_instance=RequestContext(request))


def my_news(request, template='my_news.html', page_template='articles.html'):
    title = "Home Page"
    user = request.user

    profile = UserProfileRec.objects.get(user_id=user.id)

    has_twitter = profile.has_twitter()

    from endless_pagination.templatetags import endless

    if has_twitter:
        entries, vals = profile.get_articles()
    else:
        entries = []
        vals = []

    context = {
        'has_twitter': has_twitter,
        'entries': entries,
        'vals': vals,
        'topics': topics,
        'page_template': page_template,

    }

    if request.is_ajax():
        template = page_template

    return render_to_response(template,
                              context,
                              context_instance=RequestContext(request))


def by_topic(request, template='by_topic.html', page_template='articles.html'):
    title = "Home Page"
    user = request.user

    profile = UserProfileRec.objects.get(user_id=user.id)

    has_twitter = profile.has_twitter()

    from endless_pagination.templatetags import endless

    topic_id = int(request.GET.get('t'))
    topic_name = topics[topic_id].upper()

    topic = {'id': topic_id, 'name': topic_name, 'icon': icons[topic_id], 'colour': CSS_COLOR_NAMES[topic_id]}

    if has_twitter:
        articles = sorted(
            ArticleRec.objects.with_string_topics(topic_id),
            key=lambda instance: instance.article_published,
            reverse=True)
        with_image = [(True, item) for item in articles if not (item.article_image is None or item.article_image is '')]
        no_image = [a for a in articles if a.article_image is "" or a.article_image is None]

        paired_no_image = [(False, item1, item2, item3)
                           for item1, item2, item3 in
                           list(zip(no_image[::3], no_image[1::3], no_image[2::3]))]

        entries = list(map(next,
                           random.sample([iter(with_image)]*len(with_image) +
                                         [iter(paired_no_image)]*len(paired_no_image),
                                         len(with_image)+len(paired_no_image))))

    else:
        entries = []




    context = {
        'has_twitter': has_twitter,
        'entries': entries,
        'topics': topics,
        'page_template': page_template,
        'topic': topic,


    }

    if request.is_ajax():
        template = page_template

    return render_to_response(template,
                              context,
                              context_instance=RequestContext(request))


def auth_twitter(request):
    auth = tweepy.OAuthHandler(consumer_token,
                               consumer_secret,
                               callback_url)

    try:
        redirect_twitter = auth.get_authorization_url()

    except tweepy.TweepError:
        print("Error - failed to get access token", file=sys.stderr)

    request.session['request_token'] = auth.request_token
    print(request.session['request_token'], file=sys.stderr)
    request.session.modified = True

    print(redirect_twitter, file=sys.stderr)

    return HttpResponseRedirect(redirect_twitter)


def callback(request):

    user = request.user
    print(request.get_full_path(), file=sys.stderr)

    verifier = request.GET['oauth_verifier']

    auth = tweepy.OAuthHandler(consumer_token,
                               consumer_secret)

    token = request.session.get('request_token')
    print(token, file=sys.stderr)
    auth.request_token = token
    request.session.delete('request_token')

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError as err:

        print(err, file=sys.stderr)

    profile = UserProfileRec.objects.get(user_id=user.id)
    profile.access_token = auth.access_token
    profile.access_secret = auth.access_token_secret
    profile.save()

    profile.get_twitter_topics()

    return HttpResponseRedirect('/my_news')


def get_matches(friend_ids):
    # words = get_top_followings(profile.twitter_handle)
    words = {}
    # for i in friend_ids:
    #     words[i] = get_profile_words(i)

    return words


def entry_index(request, template='myapp/entry_index.html'):
    context = {
        'entries': ArticleRec.objects.all(),
    }
    return render_to_response(
        template, context, context_instance=RequestContext(request))


def log_in(request):

    title = "Log In"
    user = request.user

    form = LogInForm(request.POST or None)

    context = {
        "template_title" : title,
        "user" :user,
        "form" :form,
    }

    if form.is_valid():
        instance = form.save(commit=False)
        if not instance.full_name:
            instance.full_name = 'Not Given'

        instance.save()

        context = {
            "template_title" : "Thank You",
        }

    return render(request, "login.html", context)


def sign_up(request):

    title = "Sign Up"
    user = request.user

    form = SignUpForm(request.POST or None)

    context = {
        "template_title" : title,
        "user": user,
        "form": form,
    }

    if form.is_valid():
        instance = form.save(commit=False)
        if not instance.full_name:
            instance.full_name = 'Not Given'

        UserProfileRec(user=user).save()
        instance.save()

        context = {
            "template_title" : "Thank You",
        }

    return render(request, "sign_up.html", context)


def analytics(request):
    # Pie Chart Info
    profile = UserProfileRec.objects.get(user=request.user)
    profile_topics = profile.get_profile()
    twitter_topics = profile_topics["twitter_topics"]
    explicit_topics = profile_topics["explicit_topics"]

    top_twitter = [(k, topics[k].upper(), v) for k, v in Counter(twitter_topics).most_common(5)]
    top_explicit = [(k, topics[k].upper(), v) for k, v in Counter(explicit_topics).most_common(int(profile.top_n))]

    twitter_colours = [CSS_COLOR_NAMES[k] for k, _, _1 in top_twitter]
    explicit_colours = [CSS_COLOR_NAMES[k] for k, _, _2 in top_explicit]


    # Bar Chart 1
    clicked_topics = [(k, topics[k].upper(), v, CSS_COLOR_NAMES[k]) for k, v in profile_topics["clicked_topics"].items() if v>0]
    has_twitter = profile.has_twitter()
    no_clicks = all([v == 0 for k, v in profile_topics["clicked_topics"].items()])


    context = {
        "top_twitter": top_twitter,
        "twitter_colours": twitter_colours,
        "top_explicit": top_explicit,
        "explicit_colours": explicit_colours,
        "clicked_topics": clicked_topics,
        "has_twitter": has_twitter,
        "no_clicks" : no_clicks,
    }

    return render(request, "analytics.html", context)


def contact(request):

    return render(request, "contact.html", {})

def help(request):

    return render(request, "help.html", {})


def get_url(request):

    form = GetTwitterURL(request.POST or None)
    context = {
        "form", form
    }

    return (request, "forms.html", context)


def execute_sql(w):

    conn = psycopg2.connect("dbname=nlstudent user=James")
    query = "select a.article_url, a.article_title, a.article_description, a.article_published from article_rec as a join word_frequency_rec as f on a.article_id = f.article_id join word_rec as w on f.word_id = w.word_id where word=%s order by frequency DESC;"

    cur = conn.cursor()

    cur.execute(query, (w,))

    a = cur.fetchall()

    return a

