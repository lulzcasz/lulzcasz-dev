from django.conf import settings
from django.forms import widgets

class TiptapWidget(widgets.Widget):
    template_name = 'blog/tiptap.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value or ''
        context['debug'] = settings.DEBUG  # Envia se estamos em dev ou prod
        return context

    @property
    def media(self):
        if settings.DEBUG:
            return widgets.Media(
                css={
                    # Troque "style.css" por "admin-editor.css"
                    'all': ('http://localhost:5173/static/css/admin-editor.css',),
                }
            )
        else:
            return widgets.Media(
                css={
                    # Troque "style.css" por "admin-editor.css"
                    'all': ('dist/css/admin-editor.css',),
                }
            )
