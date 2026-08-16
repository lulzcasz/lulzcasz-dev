from django.conf import settings
from django.forms import widgets

class TiptapWidget(widgets.Widget):
    template_name = 'blog/tiptap.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value or ''
        context['debug'] = settings.DEBUG
        return context

    @property
    def media(self):
        if settings.DEBUG:
            return widgets.Media(
                css={
                    'all': ('http://localhost:5173/static/css/admin-editor.css',),
                }
            )
        else:
            return widgets.Media(
                css={
                    'all': ('dist/css/admin-style.css',),
                }
            )
