__author__ = 'James'

from time import mktime
from dateutil import parser, tz
import datetime

class ArticleWrapper:
    def __init__(self, title, url, description, source, time):
        self.title = title
        self.url = url
        self.description = description
        self.source = source
        self.time = datetime.datetime(*(time[0:6]))
        self.content = {}
        self.tag = None
        self.img = None

    def to_string(self):
        return self.title + ", " + self.url + ", " + str(self.content)

