from django.contrib import admin
from portfolio.models import  Link, Profile, Project


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass
