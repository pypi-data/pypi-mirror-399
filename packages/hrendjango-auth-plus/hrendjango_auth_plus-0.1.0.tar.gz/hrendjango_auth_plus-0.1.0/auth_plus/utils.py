import os, requests
from dataclasses import dataclass
from django.core.exceptions import ValidationError
from django.urls import path, include
from django.conf import settings
from hrenpack.strwork import randstr
from hrendjango.utils import get_project_name
from . import TFA_WAYS


def get_avatar_filename(instance, filename):
    base_path = getattr(settings, 'AUTH_PLUS_BASE_MEDIA_FOLDER', os.path.join(settings.MEDIA_ROOT, 'auth_plus'))
    return os.path.join(base_path, 'avatars', filename)


def get_base_template():
    return getattr(settings, 'AUTH_PLUS_BASE_TEMPLATE', getattr(settings, 'BASE_TEMPLATE', 'empty.html'))


def get_default_signature():
    return f"Команда сайта {get_project_name()}"


def tfa_enabled():
    return bool(TFA_WAYS)


def user_tfa_enabled(user):
    pass
