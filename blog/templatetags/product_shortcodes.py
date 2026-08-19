import re
from django import template
from django.template.loader import render_to_string
from django.utils.translation import get_language
from products.models import Product
from blog.models import Article

register = template.Library()

ISOLATE_SHORTCODE_REGEX = re.compile(
    r'(<p[^>]*>(?:(?!</p>).)*?)(?:<br\s*/?>)?\s*\[(product|article)-(\d+)\]\s*(?:<br\s*/?>)?((?:(?!</p>).)*?</p>)',
    re.IGNORECASE | re.DOTALL
)

INLINE_SHORTCODE_REGEX = re.compile(r'\[(product|article)-(\d+)\]')

@register.filter(name='render_shortcodes')
def render_shortcodes(content):
    if not content:
        return ""

    old_content = None
    while old_content != content:
        old_content = content
        content = ISOLATE_SHORTCODE_REGEX.sub(r'\1</p>[\2-\3]<p>\4', content)

    content = re.sub(r'<p[^>]*>\s*</p>', '', content)

    def replace_with_card(match):
        shortcode_type = match.group(1) 
        item_id = match.group(2)        

        if shortcode_type == 'product':
            try:
                product = Product.objects.get(id=item_id)
                return render_to_string('blog/product.html', {'product': product})
            except Product.DoesNotExist:
                return ""
                
        elif shortcode_type == 'article':
            try:
                article = Article.objects.get(id=item_id)
                return render_to_string('blog/article.html', {'article': article})
            except Article.DoesNotExist:
                return ""
                
        return ""

    content = re.sub(INLINE_SHORTCODE_REGEX, replace_with_card, content)

    return content
