from django.contrib import admin
from about.models import  Link, Profile, HighlightPost


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(HighlightPost)
class HighlightPostAdmin(admin.ModelAdmin):
    pass
