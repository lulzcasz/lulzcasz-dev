from blog.models import Section, Category, Tag, Article
from blog.utils.paginate import paginate_queryset
from django.shortcuts import get_object_or_404, render
import uuid
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from blog.tasks.image import process_image
from blog.tasks.video import process_video
from django.utils.translation import get_language


def index(request):
    current_lang = get_language()

    last_articles = (
        Article.objects.filter(
            published_at__lte=timezone.now(),
            translations__language_code=current_lang,
        )
        .order_by("-published_at")[:3]
    )

    featured_articles = (
        Article.objects.filter(
            published_at__lte=timezone.now(),
            is_featured=True,
            translations__language_code=current_lang,
        )[:3]
    )

    ctx = {"featured_articles": featured_articles, "last_articles": last_articles}

    return render(request, "blog/index.html", ctx)


def article_detail(request, article_slug):
    current_lang = get_language()
    
    article = get_object_or_404(
        Article,
        translations__slug=article_slug,
        translations__language_code=current_lang,
        published_at__lte=timezone.now()
    )

    return render(request, 'blog/article_detail.html', {'article': article})


def articles(request):
    all_articles = Article.objects.filter(
        published_at__lte=timezone.now()
    ).order_by("-published_at")

    page_obj = paginate_queryset(request, all_articles)

    return render(
        request,
        "blog/article_list.html",
        {"page_obj": page_obj, "title": "All Articles"},
    )


def articles_by_section(request, section_slug):
    section = get_object_or_404(Section, slug=section_slug)

    articles_qs = Article.objects.filter(
        section=section, 
        published_at__lte=timezone.now()
    ).order_by("-published_at")

    page_obj = paginate_queryset(request, articles_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Gênero: {section.name}",
        "current_section": section,
    }

    return render(request, "blog/article_list.html", context)


def articles_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    articles_qs = Article.objects.filter(
        category=category, 
        published_at__lte=timezone.now()
    ).order_by("-published_at")

    page_obj = paginate_queryset(request, articles_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Categoria: {category.name}",
        "current_category": category,
    }

    return render(request, "blog/article_list.html", context)


def articles_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)

    articles_qs = Article.objects.filter(
        tags__slug=tag_slug, 
        published_at__lte=timezone.now()
    ).order_by("-published_at")

    page_obj = paginate_queryset(request, articles_qs)

    context = {
        "page_obj": page_obj,
        "title": f"Tag: #{tag.name}",
        "current_tag": tag,
    }

    return render(request, "blog/article_list.html", context)


@login_required
def tinymce_upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload = request.FILES['file']
        raw_article_uuid = request.POST.get('article_uuid')

        try:
            valid_uuid = str(uuid.UUID(raw_article_uuid))
            folder_path = f"articles/{valid_uuid}/content"
        except (ValueError, TypeError):
            date_path = timezone.now().strftime('%Y/%m/%d')
            folder_path = f"images/content/unassigned/{date_path}"

        image_token = str(uuid.uuid4())
        relative_path = f"{folder_path}/{image_token}/raw.webp"
        saved_path = default_storage.save(relative_path, upload)
        file_url = default_storage.url(saved_path)
        process_image.delay(saved_path, 'content_image')
        
        return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def tinymce_upload_video(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload = request.FILES['file']
        raw_article_uuid = request.POST.get('article_uuid')

        try:
            valid_uuid = str(uuid.UUID(raw_article_uuid))
            folder_path = f"articles/{valid_uuid}/content"
        except (ValueError, TypeError):
            date_path = timezone.now().strftime('%Y/%m/%d')
            folder_path = f"videos/content/unassigned/{date_path}"

        video_token = str(uuid.uuid4())
        relative_path = f"{folder_path}/{video_token}/raw.webm"
        saved_path = default_storage.save(relative_path, upload)
        file_url = default_storage.url(saved_path)
        process_video.delay(saved_path, 'content_video')
        
        return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)
