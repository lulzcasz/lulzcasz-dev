from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from portfolio.models import Link, Profile, Project


def index(request):
    return render(
        request,
        "portfolio/index.html",
        {
            "links": Link.objects.all(),
            "profile": Profile.objects.first(),
            "projects": Project.objects.all(),
        },
    )



def project_detail(request, project_slug):
    project = get_object_or_404(
        Project, slug=project_slug, is_published=True
    )
    profile = Profile.objects.first()

    return render(
        request, "portfolio/project_detail.html", {"project": project, "profile": profile},
    )
