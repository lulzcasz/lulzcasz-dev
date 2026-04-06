from os.path import splitext
from uuid import uuid4
from django.utils.timezone import now
from django.core.paginator import Paginator


def article_image_path(instance, filename):
    return f'images/covers/{now().strftime("%Y/%m/%d")}/{uuid4()}/raw{splitext(filename)[1]}'


def paginate_queryset(request, queryset, per_page=4):
    return Paginator(queryset, per_page).get_page(request.GET.get("pagina"))
