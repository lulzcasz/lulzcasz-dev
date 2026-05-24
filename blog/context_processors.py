from blog.models import Genre, Category, Post

def explore_items(request):
    return {
        'genres': Genre.objects.all(), 
        'categories': Category.objects.all(),
    }
