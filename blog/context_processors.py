from blog.models import Section, Category, Article

def explore_items(request):
    return {
        'sections': Section.objects.all(), 
        'categories': Category.objects.all(),
    }
