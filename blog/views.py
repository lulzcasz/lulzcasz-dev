from blog.models import Category, Format, Post
from common.utils import paginate_queryset
from django.shortcuts import get_object_or_404, render
from portfolio.models import Profile
from taggit.models import Tag


def index(request):
    last_posts = Post.objects.filter(is_published=True).order_by("-published_at")[:3]

    featured_posts = Post.objects.filter(is_published=True, is_featured=True)[:3]

    ctx = {"featured_posts": featured_posts, "last_posts": last_posts}

    return render(request, "blog/index.html", ctx)


def post_detail(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug, is_published=True)
    profile = Profile.objects.first()

    return render(
        request,
        "blog/post_detail.html",
        {"post": post, "profile": profile},
    )


def posts(request):
    all_posts = Post.objects.filter(is_published=True).order_by("-published_at")

    page_obj = paginate_queryset(request, all_posts)

    return render(
        request,
        "blog/post_list.html",
        {"page_obj": page_obj, "title": "Todos os Posts"},
    )


def posts_by_format(request, format_slug):
    post_format = get_object_or_404(Format, slug=format_slug)

    posts_qs = Post.objects.filter(post_format=post_format, is_published=True).order_by(
        "-published_at"
    )

    page_obj = paginate_queryset(request, posts_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Formato: {post_format.name}",
        "current_format": post_format,
    }

    return render(request, "blog/post_list.html", context)


def posts_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    posts_qs = Post.objects.filter(category=category, is_published=True).order_by(
        "-published_at"
    )

    page_obj = paginate_queryset(request, posts_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Categoria: {category.name}",
        "current_category": category,
    }

    return render(request, "blog/post_list.html", context)


def posts_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)

    posts_qs = Post.objects.filter(tags__slug=tag_slug, is_published=True).order_by(
        "-published_at"
    )

    page_obj = paginate_queryset(request, posts_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Tag: #{tag.name}",
        "current_tag": tag,
    }

    return render(request, "blog/post_list.html", context)
