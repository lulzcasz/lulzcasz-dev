from django.shortcuts import render
from about.models import Link, Profile
from about.models import HighlightPost


def index(request):
    return render(
        request,
        "about/index.html",
        {
            "links": Link.objects.all(),
            "profile": Profile.objects.first(),
            "highlight_posts": HighlightPost.objects.all(),
        },
    )
