from django.contrib import admin
from common.models import  Technology 

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    pass
