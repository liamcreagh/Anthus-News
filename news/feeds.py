from django.contrib.syndication.views import feedgenerator
from .models import Entry


class ArchiveFeed(feedgenerator):
    title = 'Archive Feed'
    description = 'Archive Feed'
    link = '/archive/'

    def items(self):
        return Entry

    def item_link(self, item):
        return "/archive/"

    def item_title(self):
        return item.title

    def item_description(self):
        return item.description