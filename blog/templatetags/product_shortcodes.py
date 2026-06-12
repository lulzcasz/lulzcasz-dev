import re
from django import template
from django.template.loader import render_to_string
from products.models import Product

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
