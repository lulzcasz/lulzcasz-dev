from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page=4):
    return Paginator(queryset, per_page).get_page(request.GET.get("pagina"))
