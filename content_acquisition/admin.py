from django.contrib import admin

# Register your models here.

from .models import FeedRec

class FeedAdmin(admin.ModelAdmin):
    pass

admin.site.register(FeedRec, FeedAdmin)