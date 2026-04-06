from blog.models import Format, Category, Article

def explore_items(request):
    return {
        'formats': Format.objects.all(), 
        'categories': Category.objects.all(),
    }
