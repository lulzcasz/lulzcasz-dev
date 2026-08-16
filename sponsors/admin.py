from django.contrib import admin
from sponsors.models import Sponsor
from unfold.admin import ModelAdmin


@admin.register(Sponsor)
class SponsorAdmin(ModelAdmin):
    pass
