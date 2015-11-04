from __future__ import absolute_import

from feed_aggregator import aggregate
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task


@task
def insert_articles():
    print('start')
    while True:
        aggregate()

    print('...')
    return None


@periodic_task(run_every=crontab(minute='*/30'))
def every_hour():
    aggregate()
