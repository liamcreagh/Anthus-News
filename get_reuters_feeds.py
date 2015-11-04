import operator
from sqlite3 import Date
from urllib.request import urlopen

__author__ = 'James'

from urllib import request
import re

from bs4 import BeautifulSoup
import feedparser
import json
import django
django.setup()

from content_acquisition.models import FeedRec

abc_tech = {'url':'http://feeds.abcnews.com/abcnews/technologyheadlines','source':'abcnews.com'}
bbc_tech = {'url':'http://feeds.bbci.co.uk/news/technology/rss.xml?edition=uk','source':'bbc.co.uk'}

abc_travel = {'url':'http://feeds.abcnews.com/abcnews/travelheadlines','source':'abcnews.com'}
breaking_travel = {'url':'http://feeds.feedburner.com/breakingtravelnews','source':'breakingtravelnews.com'}

telegraph_food = {'url':'http://www.telegraph.co.uk/foodanddrink/foodanddrinknews/rss','source':'telegraph.co.uk'}
telegraph_restaurant = {'url':'http://www.telegraph.co.uk/foodanddrink/restaurants/rss','source':'telegraph.co.uk'}
eatingwell = {'url':'http://feeds.feedburner.com/EatingwellBlogs-AllBlogPosts?format=xml', 'source':'eatingwell.com'}

abc_entertainment = {'url':'http://feeds.abcnews.com/abcnews/entertainmentheadlines','source': 'abcnews.com'}
reuters_entertainment = {'url':'http://mf.feeds.reuters.com/reuters/UKEntertainment','source': 'reuters.com'}
access_hollywood_entertainment = {'url':'http://feeds.accesshollywood.com/AccessHollywood/LatestNews','source':'accesshollywood.com'}

bbc_health = {'url':'http://feeds.bbci.co.uk/news/health/rss.xml?edition=uk','source':'bbc.co.uk'}
reuters_health = {'url':'http://mf.feeds.reuters.com/reuters/UKHealth','source':'reuters.com'}
reuters_health2 = {'url': 'http://mf.feeds.reuters.com/reuters/UKHealthNews','source':'reuters.com'}

bbc_pol = {'url':'http://feeds.bbci.co.uk/news/politics/rss.xml?edition=uk','source':'bbc.co.uk'}
reuters_pol = {'url':'http://feeds.reuters.com/Reuters/PoliticsNews','source':'reuters.com'}

reuters_sci = {'url':'http://mf.feeds.reuters.com/reuters/UKScienceNews','source':'reuters.com'}
bbc_sci = {'url':'http://feeds.bbci.co.uk/news/science_and_environment/rss.xml?edition=uk','source':'bbc.co.uk'}

yahoo_soc_sport = {'url':'http://sports.yahoo.com/soccer//rss.xml','source':'yahoo.com'}
yahoo_nfl_sport = {'url':'https://sports.yahoo.com/nfl/rss.xml','source':'yahoo.com'}
reuters_sport = {'url':'http://mf.feeds.reuters.com/reuters/UKSportsNews','source':'reuters.com'}
reuters_rugby = {'url':'http://mf.feeds.reuters.com/reuters/UKRugbyNews','source':'reuters.com'}

rolling_stone_music = {'url':'http://www.rollingstone.com/music.rss','source':'rollingstone.com'}
music_news = {'url':'http://www.music-news.com/rss/news.asp','source':'music-news.com'}
nme_music = {'url':'http://www.nme.com/rss/news','source':'nme.com'}

movieweb_film = {'url':'http://movieweb.com/rss/movie-news/','source':'movieweb.com'}
rolling_stone_film = {'url':'http://www.rollingstone.com/movies.rss','source':'rollingstone.com'}

rte_busi = {'url':'http://www.rte.ie/news/rss/business-headlines.xml','source':'rte.ie'}
forbes_busi = {'url':'http://www.forbes.com/markets/feed/','source':'forbes.com'}
fin_busi = {'url':'http://www.finfacts.ie/finfactsblog/atom.xml','source':'finfacts.ie'}

irish_edu = {'url':'http://www.education.ie/en/Press-Events/RSS-Feed-page/?GroupId=870&rssVersion=Rss20','source':'education.ie'}
telegraph_edu = {'url': 'http://www.telegraph.co.uk/education/educationnews/rss','source':'telegraph.co.uk'}
edweek_edu = {'url': 'http://feeds.feedburner.com/EducationWeekNewsAndInformationAboutEducationIssues','source':'eduweek.com'}

digitalarts_art = {'url': 'http://rss.feedsportal.com/c/662/f/8410/index.rss','source':'digitalarts.com'}
arts_council_art = {'url': 'http://www.artscouncil.ie/rss-feed/?searchQuery=News','source':'artscouncil.ie'}
artnews_art = {'url': 'http://www.artnews.com/feed/','source':'artnews.com'}

glamour_fashion = {'url': 'http://feeds.glamour.com/glamour/glamour_all','source': 'glamour.com'}
instyle_fashion = {'url': 'http://www.instyle.co.uk/fashion/news.rss','source': 'instyle.co.uk'}
tv_fashion = {'url': 'http://www.fashiontv.com/rss/fashion','source':'fashiontv.com'}

tmz_celeb = {'url': 'http://www.tmz.com/category/celebrity-justice/rss.xml','source': 'tmz.com'}
tmz2_celeb = {'url': 'http://www.tmz.com/category/celebrity-feuds/rss.xml','source': 'tmz.com'}

just_design = {'url': 'http://feeds.feedburner.com/JustCreativeDesignBlog','source': 'justcreative.com'}
daily_design = {'url': 'http://feeds.feedburner.com/DailyDesignerNews','source': 'designer-daily.com'}
abduzeedo_design = {'url': 'http://feeds.feedburner.com/abduzeedo', 'source':'abduzeedo.com'}



tech_feeds = [abc_tech, bbc_tech]
health_feeds = [bbc_health, reuters_health, reuters_health2]
travel_feeds = [abc_travel, breaking_travel]
entertainment_feeds = [abc_entertainment, access_hollywood_entertainment, reuters_entertainment]
pol_feeds = [bbc_pol, reuters_pol]
sci_feeds = [bbc_sci, reuters_sci]
sport_feeds = [yahoo_nfl_sport, yahoo_soc_sport, reuters_sport, reuters_rugby]
food_feeds = [telegraph_food, telegraph_restaurant,eatingwell]
music_feeds = [music_news, nme_music, rolling_stone_music]
film_feeds = [movieweb_film, rolling_stone_film]
business_feeds = [rte_busi, forbes_busi, fin_busi]
edu_feeds = [telegraph_edu, edweek_edu]
art_feeds = [arts_council_art, artnews_art]
fashion_feeds = [glamour_fashion, instyle_fashion, tv_fashion]
celebrity_feeds = [tmz2_celeb, tmz_celeb]
design_feeds = [daily_design, just_design,abduzeedo_design]

all_feeds = {'tech': tech_feeds,
             'health': health_feeds,
             'travel': travel_feeds,
             'entertainment': entertainment_feeds,
             'politics': pol_feeds,
             'science': sci_feeds,
             'sport': sport_feeds,
             'food': food_feeds,
             'music': music_feeds,
             'film': film_feeds,
             'art': art_feeds,
             'business': business_feeds,
             'education': edu_feeds,
             'fashion': fashion_feeds,
             'celebrity': celebrity_feeds,
             'design': design_feeds}


def add_feeds():
    for topic, feeds in all_feeds.items():
        for feed in feeds:
            f = feedparser.parse(feed['url'])
            print(f.feed.title)
            fr = FeedRec(feed_url=feed['url'], feed_title=f.feed.title, feed_source=feed['source'])
            fr.save()


def get_feedly_feeds():
    for topic in all_feeds:
        u = urlopen('http://cloud.feedly.com/v3/search/feeds?query=' + topic + '&count=500&locale=en')
        h = u.read().decode('utf-8')
        j = json.loads(h, encoding='utf-8')

        results = list(filter(lambda x: 20 < x['velocity'] < 150, j['results']))

        topic_vel = 0

        for r in results:
            feed_url = r['feedId'][5:]
            feed_title = r['title'][:100]
            try:
                feed_source = r['website']
            except KeyError:
                continue

            topic_vel += r['velocity']
            if topic_vel > 3000:
                break
            fr = FeedRec(feed_url=feed_url, feed_title=feed_title, feed_source=feed_source)
            fr.save()
        print(topic, len(results), topic_vel)


get_feedly_feeds()

def add_reuters_to_db():

    url_list = []
    reuters_urls = ['http://uk.reuters.com/tools/rss', 'http://www.reuters.com/tools/rss']

    for url in reuters_urls:

        doc = request.urlopen(url)

        soup = BeautifulSoup(doc)

        for s in soup.find_all('td', 'feedUrl'):
            m = re.search('(?<=//)(.*)', s.text)
            url_list.append("http://" + m.groups()[0])

        for u in url_list:
            print(u)
            f = feedparser.parse(u)
            if not f.feed.updated_parsed.tm_year < Date.today().year:

                fr = FeedRec(feed_url=u, feed_title=f.feed.title)
                fr.save()

