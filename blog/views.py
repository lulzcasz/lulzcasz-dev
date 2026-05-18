from django.shortcuts import get_object_or_404, render
from blog.models import Format, Category, Tag, Post
from blog.utils import paginate_queryset
import os
from uuid import uuid4
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from blog.tasks.image import process_image
from about.models import Profile


@login_required
def tinymce_upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload = request.FILES['file']

        date_path = timezone.now().strftime('%Y/%m/%d')
        token = str(uuid4())
        _, ext = os.path.splitext(upload.name)

        relative_path = f"images/content/{date_path}/{token}/raw{ext}"

        saved_path = default_storage.save(relative_path, upload)
        file_url = default_storage.url(saved_path)

        process_image.delay(saved_path, 'content_image')
        
        return JsonResponse({'location': file_url})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def index(request):
    last_posts = Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).order_by("-published_at")[:3]

    featured_posts = Post.objects.filter(
        status=Post.Status.PUBLISHED, 
        is_featured=True
    )[:3]

    ctx = {"featured_posts": featured_posts, "last_posts": last_posts}

    return render(request, "blog/index.html", ctx)


def post_detail(request, post_slug):
    post = get_object_or_404(
        Post, slug=post_slug, status=Post.Status.PUBLISHED
    )
    profile = Profile.objects.first()

    return render(
        request, "blog/post_detail.html", {"post": post, "profile": profile},
    )


def posts(request):
    all_posts = Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).order_by("-published_at")

    page_obj = paginate_queryset(request, all_posts)

    return render(
        request,
        "blog/post_list.html",
        {
            "page_obj": page_obj, 
            "title": "Todos os Posts"
        },
    )

def posts_by_format(request, format_slug):
    post_format = get_object_or_404(Format, slug=format_slug)

    posts_qs = Post.objects.filter(
        post_format=post_format, 
        status=Post.Status.PUBLISHED
    ).order_by("-published_at")

    page_obj = paginate_queryset(request, posts_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Formato: {post_format.name}",
        "current_format": post_format,
    }

    return render(request, "blog/post_list.html", context)


def posts_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    posts_qs = Post.objects.filter(
        category=category, 
        status=Post.Status.PUBLISHED
    ).order_by("-published_at")

    page_obj = paginate_queryset(request, posts_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Categoria: {category.name}",
        "current_category": category,
    }

    return render(request, "blog/post_list.html", context)


def posts_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)

    posts_qs = Post.objects.filter(
        tags=tag, 
        status=Post.Status.PUBLISHED
    ).order_by("-published_at")

    page_obj = paginate_queryset(request, posts_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Tag: #{tag.name}",
        "current_tag": tag,
    }

    return render(request, "blog/post_list.html", context)
