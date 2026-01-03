from django.conf import settings
from hrenpack.listwork import mislist
from .constants import DEFAULT_TFA_WAYS

TFA_WAYS = getattr(settings, 'AUTH_PLUS_TFA_WAYS', DEFAULT_TFA_WAYS)


def include_auth_plus_app(apps_list) -> list:
    """Используйте INSTALLED_APPS += include_auth_plus_app(INSTALLED_APPS)"""
    return mislist(
        apps_list,
        'django_recaptcha.apps.DjangoRecaptchaConfig',
        'hrendjango.apps.HrendjangoConfig',
        'auth_plus.apps.AuthPlusConfig'
    )
