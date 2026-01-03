from typing import Literal
from django.conf import settings
from django.template import Library
from django.template.exceptions import TemplateSyntaxError

register = Library()


@register.inclusion_tag('auth_plus/includes/recaptcha.html')
def recaptcha(version: Literal[2, 3], theme: Literal['light', 'dark'] = 'light'):
    if version not in (2, 3):
        raise TemplateSyntaxError("Неправильная версия recaptcha")
    site_key = settings.RECAPTCHA_PUBLIC_KEY if version == 2 else settings.RECAPTCHA_V3_PUBLIC_KEY
    return dict(version=version, theme=theme, site_key=site_key)
