from blog.models import Kind, Category, Article

def explore_items(request):
    return {
        'kinds': Kind.objects.all(), 
        'categories': Category.objects.all(),
    }
