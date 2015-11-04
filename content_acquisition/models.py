from __future__ import unicode_literals

from django.db import models


# Create your models here.

class FeedRec(models.Model):
    feed_url = models.CharField(max_length=200, primary_key=True)
    feed_title = models.CharField(max_length=100)
    feed_etag = models.CharField(max_length=100)
    feed_modified = models.CharField(max_length=100,blank=True, null=True)
    feed_source = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'feed_rec'
