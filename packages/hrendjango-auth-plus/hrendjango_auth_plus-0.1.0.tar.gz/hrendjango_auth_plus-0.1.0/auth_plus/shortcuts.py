from django.conf import settings
from django.urls import path, include


def auth_plus_urls_namespace():
    return getattr(settings, 'AUTH_PLUS_URLS_NAMESPACE', '')


def auth_plus_urls(url: str):
    return [path(url, include('auth_plus.urls', auth_plus_urls_namespace()))]