from django.contrib import admin
from about.models import  Link, Profile, HighlightArticle


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(HighlightArticle)
class HighlightArticleAdmin(admin.ModelAdmin):
    pass
