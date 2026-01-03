import uuid
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from .base import *
from .validators import *
from .managers import *
from .generators import *
from .otp import *
from ..constants import AUTH_PLUS_EMAIL_VERIFICATION_CODE_PERIOD


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        abstract = False
        swappable = "AUTH_USER_MODEL"


class ConfirmationCode(models.Model):
    """
    Типы кодов:\n
    email_verification: Подтверждение адреса электронной почты\n
    password_reset: Сброс пароля
    """
    email = models.EmailField(verbose_name="Адрес электронной почты")
    type = models.CharField(max_length=32, verbose_name="Тип кода")
    code = models.CharField(max_length=6, default=generate_confirmation_code, validators=[MinLengthValidator(6)],
                            verbose_name="Код")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_used = models.BooleanField(default=False, verbose_name="Использован")
    token = models.UUIDField(default=uuid.uuid4)

    objects = models.Manager()
    new = NotUsedManager()

    def is_valid(self):
        max_period = AUTH_PLUS_EMAIL_VERIFICATION_CODE_PERIOD
        # getattr(settings, 'AUTH_PLUS_EMAIL_VERIFICATION_CODE_PERIOD', 600)
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < max_period

    class Meta:
        verbose_name = "код подтверждения"
        verbose_name_plural = "Коды подтверждения"
        ordering = ['-created_at']
