"""pinkproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    #Home Page (index.html)
    url(r'^$', 'news.views.index', name='index'),

    #Test Development Pages

    url(r'^admin/', include(admin.site.urls)),
    url(r'^main_news/', 'news.views.main_news', name='main_news'),
    # url(r'^add_twitter', 'news.views.add_twitter', name='liam_home'),
    url(r'^my_news/', 'news.views.my_news', name='my_news'),
        url(r'^by_topic/', 'news.views.by_topic', name='by_topic'),


    url(r'^analytics/', 'news.views.analytics', name='analytics'),
    url(r'^contact/', 'news.views.contact', name='contact'),
    url(r'^callback', 'news.views.callback', name='callback'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^my_profile/', 'user_profile.views.my_profile', name='my_profile'),

    # ajax methods

    url(r'^update_profile/', 'user_profile.views.update_profile'),
    url(r'^update_clicks/', 'user_profile.views.update_clicks'),
    url(r'^help/', 'news.views.help'),



    url(r'^update_twitter/', 'user_profile.views.update_twitter'),

    url(r'^auth_twitter/', 'news.views.auth_twitter', name='auth_twitter'),




] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


