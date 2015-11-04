from operator import itemgetter
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import re
from .models import UserProfileRec, topics


@csrf_exempt
def update_profile(request):

    """
    update explicit ratings from ajax request
    """

    percents = {}

    profile = UserProfileRec.objects.get(user=request.user)

    for k, v in request.POST.items():
        i = re.search(r'(?<=\[)(.*)(?=\])', k).groups()[0]

        percents[int(i)] = int(v[:-1])
    profile.update("explicit_topics", {t: 0 for t, _ in enumerate(topics)})
    profile.update("explicit_topics", percents)

    if len(percents)>=5:
        profile.top_n = len(percents)
    else:
        profile.top_n = 5

    profile.save()

    return HttpResponse('', mimetype='application/json')


@csrf_exempt
def update_twitter(request):

    """
    update twitter ratings from ajax request
    """

    if request.is_ajax():
        profile = UserProfileRec.objects.get(user=request.user)
        profile.get_twitter_topics()
        profile.top_n = 5

        profile.save()

    return HttpResponse('', mimetype='application/json')


@csrf_exempt
def update_clicks(request):

    """
    update clicked ratings from ajax request
    """

    if request.is_ajax():
        profile = UserProfileRec.objects.get(user=request.user)
        tag = request.POST.get("tag")
        profile.update("clicked_topics", {topics.index(tag.lower()): 1})
        print("Clicked:", tag)
    return HttpResponse('', mimetype='application/json')


def my_profile(request):

    """
    Provide context for profile (slider initialisation)
    """

    profile = UserProfileRec.objects.get(user=request.user)
    profile_topics = profile.get_profile()

    explicit_topics = sorted([(k, topics[k], v) for k, v in profile_topics["explicit_topics"].items()],
                             key=itemgetter(2), reverse=True)

    my_interests = explicit_topics[:int(profile.top_n)]
    suggested_interests = explicit_topics[int(profile.top_n):]

    context = {
        "my_interests": my_interests,
        "suggested_interests": suggested_interests,
        "has_twitter": profile.has_twitter(),
        "twitter_image": profile.profile_image,
        "twitter_handle": profile.profile_handle,
        "twitter_name": profile.profile_name

    }

    return render(request, "my_profile.html", context)
