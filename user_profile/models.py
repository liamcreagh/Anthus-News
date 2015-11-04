import base64
from collections import Counter, defaultdict
from itertools import chain, groupby
from math import ceil
from pprint import pprint
from scipy.special import expit
import operator
import random
from django.db import models
from django.contrib.auth.models import User
from gensim.corpora import MmCorpus, Dictionary
import pickle
import numpy as np
from registration.signals import user_registered

# Create your models here.
from sklearn.preprocessing import normalize
import sys
import tweepy
from articles.models import ArticleRec, topics

consumer_token = '0LA4gRkTxqKisEBBUia2n6ycc'
consumer_secret = 'WERUhw4tLvYVIDpCkB9hqE9ExBVOVhDDtVrSSwm1wO91mTHjpW'
try:
    list_dict = Dictionary.load('/home/nlstudent/pink-news/Pink-Team/topic_modelling/terms.dict')

    corp_50 = MmCorpus('/home/nlstudent/pink-news/Pink-Team/topic_modelling/expert_corpus.mm')
    expert_map_50 = pickle.load(open('/home/nlstudent/pink-news/Pink-Team/topic_modelling/expert2doc.p', 'rb'))

    corp_10 = MmCorpus('/home/nlstudent/pink-news/Pink-Team/topic_modelling/expert_corpus_under_50.mm')
    expert_map_10 = pickle.load(open('/home/nlstudent/pink-news/Pink-Team/topic_modelling/expert2doc_under_50.p', 'rb'))
except FileNotFoundError:
    list_dict = Dictionary.load('./topic_modelling/terms.dict')

    corp_50 = MmCorpus('./topic_modelling/expert_corpus.mm')
    expert_map_50 = pickle.load(open('./topic_modelling/expert2doc.p', 'rb'))

    corp_10 = MmCorpus('./topic_modelling/expert_corpus_under_50.mm')
    expert_map_10 = pickle.load(open('./topic_modelling/expert2doc_under_50.p', 'rb'))

doc2expert_10 = {v: k for k, v in expert_map_10.items()}
doc2expert_50 = {v: k for k, v in expert_map_50.items()}


class UserProfileRec(models.Model):
    class Meta:
        db_table = 'profile_rec'


    user = models.OneToOneField(User, primary_key=True)
    access_token = models.TextField(max_length=50, blank=True, null=True)
    access_secret = models.TextField(max_length=50, blank=True, null=True)

    profile_image = models.TextField(max_length=200, blank=True, null=True)
    profile_name = models.TextField(max_length=50, blank=True, null=True)
    profile_handle = models.TextField(max_length=50, blank=True, null=True)

    profile_topics = models.TextField(null=True)
    num_clicks = models.IntegerField(default=0)
    top_n = models.IntegerField(default=5)

    def has_twitter(self):
        """
        :return: true if the user has authorized with twitter
        """

        return self.access_token is not None

    def init_auth(self):
        """
        :return: authenticated Tweepy api object
        """

        auth = tweepy.OAuthHandler(consumer_token,
                                   consumer_secret)

        auth.set_access_token(self.access_token,
                              self.access_secret)

        api = tweepy.API(auth)

        return api


    def get_twitter_list(self, api):
        """
        :param api: user-authenticated Tweepy api object
        :return: list of friend ids from twitter
        """

        friends = api.friends_ids()

        return friends

    def get_twitter_info(self, api):
        """
        :param api: user-authenticated Tweepy api object

        Updates database records for user with Twitter avatar, screen name and profile name

        """

        me = api.me()

        print("twitter info: ", me.profile_image_url, me.screen_name)

        self.profile_image = me.profile_image_url
        self.profile_name = me.name
        self.profile_handle = me.screen_name

        self.save(update_fields=['profile_name', 'profile_image', 'profile_handle'])

    def get_profile(self):
        """
        :return: dict representing twitter, explicit and click ratings
        """

        return pickle.loads(base64.b64decode(self.profile_topics))

    def update(self, entry, value):

        """
        :param entry: one of twitter_topics, explicit_topics, clicked_topics, shown_topics
        :param value: the new values for the ratings for "entry"

        Updates the specified ratings dict
        """

        profile = self.get_profile()

        if entry == "explicit_topics":
            self.top_n = 5

        profile[entry].update(value)

        print(profile)

        self.profile_topics = base64.b64encode(pickle.dumps(profile))
        self.save()

    def get_twitter_topics(self):
        """
        Loads Tweepy api, get users' friends and info and resets profile ratings
        """

        id2word = {v: k for k, v in list_dict.token2id.items()}

        self.update("twitter_topics",  {topics.index(t): 0 for t in topics})
        self.update("explicit_topics",  {topics.index(t): 0 for t in topics})

        my_votes = Counter()

        api = self.init_auth()

        self.get_twitter_info(api)

        for member in self.get_twitter_list(api):
            try:
                all_topics = sorted(corp_50[expert_map_50[member]], key=operator.itemgetter(1), reverse=True)
                t = 5
                for k, v in all_topics:
                    for topic in topics:
                        if id2word[k].startswith(topic):
                            my_votes.update({topics.index(topic): t})
                            t -= 1
                            continue

                        if t < 0:
                            break
            except KeyError:
                try:
                    all_topics = sorted(corp_10[expert_map_10[member]], key=operator.itemgetter(1), reverse=True)
                    t = 5
                    for k, v in all_topics:
                        for topic in topics:
                            if id2word[k].startswith(topic):
                                my_votes.update({topics.index(topic): t})
                                t -= 1
                                continue

                            if t < 0:
                                break
                except KeyError:
                    continue

        range1 = float(max(my_votes.values()) - min(my_votes.values()))

        normalised_votes = {}

        for k, v in my_votes.items():
            a = 100.0 * (float(v) - float(min(my_votes.values()))) / float(range1)
            normalised_votes[k] = round(a)

        self.update("twitter_topics", normalised_votes)
        self.update("explicit_topics", normalised_votes)

    def get_articles(self):

        """
        :return: list of ranked articles for a profile, with a distribution matching user preferences
        """

        all_topics = self.get_profile()

        """
        compute weights for clicks and twitter using sigmoid and inverse sigmoid respectively
        """

        weights = np.array([1.0*expit(-(0.02 * float(self.num_clicks) - 5)),
                            2.0,
                            1.0*expit(0.02 * float(self.num_clicks) - 5)])

        twitter = [float(v) for _, v in all_topics["twitter_topics"].items()]
        twitter = np.array(twitter)/sum(twitter)

        explicit = [float(v) for _, v in all_topics["explicit_topics"].items()]
        explicit = np.array(explicit)/sum(explicit)

        click = [float(v) for _, v in all_topics["clicked_topics"].items()]
        shown = [float(v) for _, v in all_topics["shown_topics"].items()]

        w_click = np.array(click)/np.array(shown)
        w_click = w_click/sum(w_click)

        m = np.vstack((twitter, explicit, w_click))

        """
        weight each rating set
        """

        percents = m * weights[:, np.newaxis]
        mdat = np.ma.masked_array(percents, np.isnan(percents))
        mm = np.sum(mdat, axis=0)

        article_tags = mm/sum(mm)

        article_tags_int = np.rint(article_tags).flatten().tolist()

        prefs = [(i, m) for i, m in enumerate(article_tags) if m > 0]

        self.update("shown_topics", {k: int(v) for k, v in enumerate(article_tags)})

        sum_prefs = sum([p[1] for p in prefs])

        """
        get 1000 articles
        """

        N_articles = 1000

        prefs = [(t, ceil(N_articles*v/sum_prefs)) for t, v in prefs]
        prefs = sorted(prefs, key=operator.itemgetter(1), reverse=True)

        num_topics = len(prefs)

        articles = []

        for tag, value in prefs:
            news = ArticleRec.objects.with_string_topics(tag)[:int(value)]
            sz = ceil(float(len(news))/(10*float(num_topics)))
            n = [news[i:i+sz] for i in range(0, len(news), sz)]
            articles.append(n)

        """
        chunk articles so that highest-rated topic is always at top of feed
        """

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

        checked = []
        rank = []
        for e in ranked_articles:
            if e.article_title not in checked:
                checked.append(e.article_title)
                rank.append(e)

        ranked_articles = rank

        """
        find articles with no images (formatted differently on frontend)
        """
        with_image = [(True, item) for item in ranked_articles if not (item.article_image is None or item.article_image is '')]
        no_image = [a for a in ranked_articles if a.article_image is "" or a.article_image is None]

        paired_no_image = [(False, item1, item2, item3) for item1, item2, item3 in list(zip(no_image[::3], no_image[1::3], no_image[2::3]))]

        b, a = sorted((with_image, paired_no_image), key=len)

        if not len(b):
            return a ,[]
        elif not len(a):
            return b, []

        len_ab = len(a) + len(b)

        """
        insert groups of imageless articles into feed
        """

        groups = groupby(((a[len(a)*i//len_ab], b[len(b)*i//len_ab]) for i in range(len_ab)),
                         key=lambda x: x[0])

        article_list = [j[i] for k, g in groups for i, j in enumerate(g)]

        return article_list, [(tag, topics[tag], value) for tag, value in enumerate(article_tags)]


def user_registered_callback(sender, user, request, **kwargs):
    """
    :param user: user_auth model object
    Callback to create profile when creating a user auth object
    """
    profile = UserProfileRec(user=user)

    """
    initialise profile ratings
    """
    profile_topics = {"twitter_topics": {topics.index(t): 0 for t in topics},
                      "explicit_topics": {topics.index(t): 0 for t in topics},
                      "clicked_topics": Counter({topics.index(t): 0 for t in topics}),
                      "shown_topics": Counter({topics.index(t): 0 for t in topics})}

    profile.profile_topics = base64.b64encode(pickle.dumps(profile_topics))

    profile.save()

"""
connect callback to registration event
"""
user_registered.connect(user_registered_callback)
