from django.db import models
from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from django.utils.translation import gettext_lazy
from .validators import *
from ..utils import get_avatar_filename

__all__ = ['AbstractUser']


class AbstractUser(DjangoAbstractUser):
    avatar = models.ImageField(upload_to=get_avatar_filename, blank=True, null=True,
                               verbose_name=gettext_lazy('Avatar'), validators=[validate_image_size])
    birth_date = models.DateField(null=True, blank=True, verbose_name=gettext_lazy('Birth Date'), validators=[validate_birth_date])
    gender = models.CharField(max_length=10, null=True, blank=True, verbose_name=gettext_lazy('Gender'))
    email_verified = models.BooleanField(default=False, verbose_name=gettext_lazy("Email verified"))

    def get_full_name(self):
        first_name = self.first_name
        last_name = self.last_name
        username = self.username
        if first_name and last_name:
            full_name = first_name + ' ' + last_name
        elif first_name:
            full_name = first_name
        else:
            full_name = username
        return full_name

    class Meta(DjangoAbstractUser.Meta):
        abstract = True
