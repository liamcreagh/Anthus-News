import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time
import tweepy
from tweepy.error import *

__author__ = 'James'

from nltk import FreqDist, RegexpTokenizer


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


stop = stopwords.words('english')
tokenizer = RegexpTokenizer(r'\w+')


class TwitterGrabber:
    keys = [AttrDict({'consumer_key': 'JuyMOBmp0go7VPbGru2fH2p7k',
                      'consumer_secret': 'EKrLiYE3LTzX4g0EyRbMRyalFkh06DMpwEikScUsQ2HAYSBqTe',
                      'access_key': '469948431-9lgLpSTnOaSbZ8cEYMB44ObErPgkViyahye7bAux',
                      'access_secret': 'oVd90UxfDJ4xA6yxznmUNJM4R80KfNErofQx53oTiTJzk'}),

            AttrDict({'consumer_key': 'JuyMOBmp0go7VPbGru2fH2p7k',
                      'consumer_secret': 'EKrLiYE3LTzX4g0EyRbMRyalFkh06DMpwEikScUsQ2HAYSBqTe',
                      'access_key': '469948431-9lgLpSTnOaSbZ8cEYMB44ObErPgkViyahye7bAux',
                      'access_secret': 'oVd90UxfDJ4xA6yxznmUNJM4R80KfNErofQx53oTiTJzk'})
            ]

    key_id = 0

    def initialise_api(self, key_set_id):
        key_set = self.keys[key_set_id]
        print(key_set)
        auth = tweepy.OAuthHandler(key_set.consumer_key, key_set.consumer_secret)
        auth.set_access_token(key_set.access_key, key_set.access_secret)
        api = tweepy.API(auth)

        return api

    def get_friends(self, user_id):
        api = self.initialise_api(self.key_id)
        user = api.get_user(id=user_id)

        print(user.screen_name)

        for friend in user.friends():
            try:
                lists = self.get_lists(friend)
                friend_id = friend.id
                print(friend_id)
            except TweepError as err:
                self.handle_tweep_error(err)

    def get_lists(self, friend):
        return friend.lists_memberships(count=50)

    def handle_tweep_error(self, err):
        if err.reason[-4:] == '429':
            self.key_id += 1


t = TwitterGrabber()
t.get_friends(12)


def get_top_followings(screen_name):
    # authorize twitter, initialize tweepy

    api = TwitterGrabber.initialise_api(0)

    print(api.get_status)

    # initialize a list to hold all the tweepy Tweets
    all_tweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    # get the user object
    # user = api.get_user(screen_name=screen_name)
    # print(user.lists_subscriptions)

    # save most recent tweets
    all_tweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = all_tweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) < 0:
        # print("getting tweets before %s" % oldest)

        # all subsequent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

        # save most recent tweets
        all_tweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = all_tweets[-1].id - 1

        print("...%s tweets downloaded so far" % (len(all_tweets)))

    tweet_text = []

    for tweet in all_tweets:
        tweet_text.append(tweet.text)

    content = []
    retweets = []

    for tweet in tweet_text:
        words = word_tokenize(tweet, 'english')
        content.extend(strip_words(words))

        if words[0] == 'RT':
            retweets.append(words[2])

    tweet_distribution = FreqDist(retweets)

    print(tweet_distribution.most_common(20))

    a = follow_description(api, tweet_distribution.most_common(20), screen_name)

    return a


def follow_description(api, friend_list, screen_name):
    the_list = []
    all_tags = []

    for friend in friend_list:
        username = friend[0]
        frequency = friend[1]

        print(username)

        try:
            user = api.get_user(screen_name=username)
            for list_obj in user.lists_memberships(screen_name=username, count=50):
                for w in list_obj.name.lower().split(" "):
                    # print(w)
                    all_tags.append(w)

        except TweepError as err:
            print(err.reason)
            break

    # print(all_tags)
    the_list_name = strip_words(all_tags)
    the_list_dist = FreqDist(the_list_name)

    # for w in the_list_dist:
    #     print ('***' + str(w))

    print(the_list_dist.most_common(20))
    return the_list_dist.most_common(20)


def strip_words(the_list_name):
    stop_words = load_stopwords()
    the_list_name = [w for w in the_list_name if not (
    re.match(r'^\W+$|^[x]|^[b?]|^[rt]|^http|^co|^\d|^\w+\d$|^amp|^\w{1,2}\w$|^\w{1}$', w) != None)]
    the_list_name = [w for w in the_list_name if not w in stop_words]
    the_list_name = [w.strip("['").strip("']").strip() for w in the_list_name]

    return the_list_name


def load_stopwords():
    stop_words = stopwords.words('english')
    stop_words.extend(['this', 'that', 'the', 'might', 'have', 'been', 'from', ' ',
                       'but', 'they', 'will', 'has', 'having', 'had', 'how', 'went'
                                                                             'were', 'why', 'and', 'still', 'his',
                       'her', 'was', 'its', 'per', 'cent',
                       'a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among',
                       'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can',
                       'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every',
                       'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his',
                       'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let',
                       'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'nor',
                       'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said',
                       'say', 'says', 'she', 'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their',
                       'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us',
                       'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who',
                       'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your', 've', 're', 'rt', 'retweet',
                       '#fuckem', '#fuck',
                       'fuck', 'ya', 'yall', 'yay', 'youre', 'youve', 'ass', 'factbox', 'com', '&lt', 'th',
                       'retweeting', 'dick', 'fuckin', 'shit', 'via', 'fucking', 'shocker', 'wtf', 'hey', 'ooh',
                       'rt&amp', '&amp',
                       '#retweet', 'retweet', 'goooooooooo', 'hellooo', 'gooo', 'fucks', 'fucka', 'bitch', 'wey',
                       'sooo', 'helloooooo', 'lol', 'smfh'])
    return stop_words
