from blog.models import Category, Kind, Article
from common.utils.paginate import paginate_queryset
from django.shortcuts import get_object_or_404, render
from portfolio.models import Profile
from taggit.models import Tag


def index(request):
    last_articles = Article.objects.filter(is_published=True).order_by("-published_at")[:3]

    featured_articles = Article.objects.filter(is_published=True, is_featured=True)[:3]

    ctx = {"featured_articles": featured_articles, "last_articles": last_articles}

    return render(request, "blog/index.html", ctx)


def article_detail(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug, is_published=True)
    profile = Profile.objects.first()

    return render(
        request,
        "blog/article_detail.html",
        {"article": article, "profile": profile},
    )


def articles(request):
    all_articles = Article.objects.filter(is_published=True).order_by("-published_at")

    page_obj = paginate_queryset(request, all_articles)

    return render(
        request,
        "blog/article_list.html",
        {"page_obj": page_obj, "title": "All Articles"},
    )


def articles_by_kind(request, kind_slug):
    kind = get_object_or_404(Kind, slug=kind_slug)

    articles_qs = Article.objects.filter(kind=kind, is_published=True).order_by(
        "-published_at"
    )

    page_obj = paginate_queryset(request, articles_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Gênero: {kind.name}",
        "current_kind": kind,
    }

    return render(request, "blog/article_list.html", context)


def articles_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    articles_qs = Article.objects.filter(category=category, is_published=True).order_by(
        "-published_at"
    )

    page_obj = paginate_queryset(request, articles_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Categoria: {category.name}",
        "current_category": category,
    }

    return render(request, "blog/article_list.html", context)


def articles_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)

    articles_qs = Article.objects.filter(tags__slug=tag_slug, is_published=True).order_by(
        "-published_at"
    )

    page_obj = paginate_queryset(request, articles_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Tag: #{tag.name}",
        "current_tag": tag,
    }

    return render(request, "blog/article_list.html", context)
