from django.shortcuts import render
from about.models import Link, Profile
from about.models import HighlightArticle


def index(request):
    return render(
        request,
        "about/index.html",
        {
            "links": Link.objects.all(),
            "profile": Profile.objects.first(),
            "highlight_articles": HighlightArticle.objects.all(),
        },
    )
