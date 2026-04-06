from django.urls import path
from about.views import index

urlpatterns = [
    path('sobre/', index, name="about"),
]
