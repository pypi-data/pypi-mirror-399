from django.db import models
from django.utils.translation import gettext_lazy


class TwoFactorAuthenticationMixin(models.Model):
    tfa_email_enabled = models.BooleanField(default=False, verbose_name=gettext_lazy(
        "Two-factor authentication is enabled by email"))
    tfa_otp_enabled = models.BooleanField(default=False, verbose_name=gettext_lazy(
        "Two-factor authentication is enabled by TOTP"))
    tfa_recovery_code_enabled = models.BooleanField(default=False, verbose_name=gettext_lazy(
        "Two-factor authentication is enabled by recovery code"))
