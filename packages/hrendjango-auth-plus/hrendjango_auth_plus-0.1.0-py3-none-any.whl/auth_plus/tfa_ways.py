from typing import Optional
from django.conf import settings
from django.utils.safestring import mark_safe
from django.views import View as DjangoView
from hrenpack.framework.django import url_or_reverse


class TwoFactorAuthenticationWay:
    __slots__ = ('id', 'enable_setting_name', 'text', 'url_setting_name', 'default_url', 'url_kwargs', 'view',
                 'user_field_name', 'security_level')

    def __init__(self, id: str, enable_setting_name: str, url_setting_name: str, default_url: str, text: str,
                 user_field_name: str, view: Optional[type] = None, url_kwargs: Optional[dict] = None) -> None:
        self.id = id
        self.enable_setting_name = enable_setting_name
        self.text = text
        self.default_url = default_url
        self.url_setting_name = url_setting_name
        self.user_field_name = user_field_name
        self.view = view if view is not None else DjangoView
        self.url_kwargs = url_kwargs if url_kwargs is not None else dict()

    def __str__(self) -> str:
        return self.text

    def __bool__(self):
        return getattr(settings, self.enable_setting_name, False)

    @property
    def url(self):
        return url_or_reverse(getattr(settings, self.url_setting_name, self.default_url), **self.url_kwargs)

    def render(self) -> str:
        return mark_safe(f'{self.text}' if getattr(settings, self.enable_setting_name, False) else '')

    def dispatch(self, request, *args, **kwargs):
        if issubclass(self.view, DjangoView):
            return self.view.dispatch(request, *args, **kwargs)
        return self.view(request, *args, **kwargs)

    def tfa_user_enabled(self, user) -> bool:
        return bool(self) and getattr(user, self.user_field_name, False)


class TwoFactorAuthenticationWays:
    _dictionary: dict = dict()

    def __init__(self, *ways):
        self._dictionary = {way.id: way for way in ways}

    def __getitem__(self, key):
        return self._dictionary[key]

    def keys(self):
        return self._dictionary.keys()

    def values(self):
        return self._dictionary.values()

    def __iter__(self):
        output = list()
        for way in self.values():
            if getattr(settings, way.enable_setting_name, False):
                output.append(way)
        return iter(output)

    def __len__(self):
        return len(self._dictionary)

    def items(self):
        return self._dictionary.items()

    def __bool__(self):
        return bool(tuple(self))
