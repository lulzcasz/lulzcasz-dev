from blog.models import Format, Category, Post

def explore_items(request):
    return {
        'formats': Format.objects.all(), 
        'categories': Category.objects.all(),
    }
