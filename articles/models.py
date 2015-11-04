from __future__ import unicode_literals

from django.db import models

topics = ['art', 'business', 'celebrity', 'design', 'education', 'entertainment', 'fashion', 'film', 'food', 'health', 'music', 'politics', 'science', 'sport', 'tech', 'travel']
CSS_COLOR_NAMES = ["#C30CBB","#D65AD1","#CB31C4","#A3009C","#7E0078","#ED0F4E","#F3658E","#EF3A6E","#DD003F","#AA0031","#671CC5","#9865D8","#7D3FCC","#4F0AA6","#3D0880","Indigo"]
icons = ["fa fa-paint-brush", "fa fa-briefcase", "fa fa-users", "fa fa-pencil", "fa fa-graduation-cap", "fa fa-star", "fa fa-diamond", "fa fa-film", "fa fa-cutlery","fa fa-heartbeat","fa fa-music","fa fa-university","fa fa-flask","fa fa-futbol-o", "fa fa-laptop", "fa fa-plane"]

topic_tags = {t: {'id': t, 'name': name, 'icon': icons[t], 'colour': CSS_COLOR_NAMES[t]} for t, name in enumerate(topics)}


class ArticleManager(models.Manager):
    def with_string_topics(self, topic_id):
        initial = super(ArticleManager, self).get_queryset()\
            .exclude(article_tag=None)\
            .filter(article_tag=topic_id)\
            .order_by("-article_published")

        for item in initial:
            topic = int(item.article_tag)
            item.article_tag = topic_tags[topic]
        return initial


class ArticleRec(models.Model):
    article_id = models.AutoField(primary_key=True)
    article_url = models.TextField(blank=True, null=True)
    article_title = models.TextField(blank=False, null=True)
    article_description = models.TextField(blank=False, null=True)
    article_source = models.TextField(blank=False, null=True)
    article_tag = models.IntegerField(blank=False, null=True)
    article_image = models.TextField(blank=False, null=True)
    article_published = models.DateTimeField(null=True)

    objects = ArticleManager()

    class Meta:
        db_table = 'article_rec'

