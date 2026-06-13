import re
from django import template
from django.template.loader import render_to_string
from products.models import Product
from blog.models import Post

register = template.Library()

SHORTCODE_REGEX = re.compile(r'\[product-(\d+)\]')

@register.filter(name='render_product_shortcodes')
def render_product_shortcodes(content):
    if not content:
        return ""

    def replace_with_card(match):
        product_id = match.group(1)
        try:
            product = Product.objects.get(id=product_id)

            return render_to_string('blog/product.html', {'product': product})
            
        except Product.DoesNotExist:
            return f""

    return re.sub(SHORTCODE_REGEX, replace_with_card, content)

WRAPPED_POST_REGEX = re.compile(r'<p[^>]*>\s*\[post-(\d+)\]\s*</p>')

INLINE_POST_REGEX = re.compile(r'\[post-(\d+)\]')

@register.filter(name='render_post_shortcodes')
def render_post_shortcodes(content):
    if not content:
        return ""

    def replace_with_card(match):
        post_id = match.group(1)
        try:
            post = Post.objects.get(id=post_id)
            return render_to_string('blog/post.html', {'post': post})
        except Post.DoesNotExist:
            return ""

    content = re.sub(WRAPPED_POST_REGEX, replace_with_card, content)

    content = re.sub(INLINE_POST_REGEX, replace_with_card, content)

    return content
