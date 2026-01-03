from django.conf import settings
from django.utils.translation import gettext_lazy
from hrenpack.framework.django import url_or_reverse
from hrenpack.framework.django.views import View
from .base import BaseSendAndVerifyView
from ..mixins import TwoFactorAuthMixin


class EmailTwoFactorAuthenticateView(TwoFactorAuthMixin, BaseSendAndVerifyView):
    email_template_name = 'auth_plus/email/two-factor-auth.html'
    template_name = 'auth_plus/verification_code/tfa_verification_code.html'
    confirmation_code_type = 'two_factor_auth'
    title = gettext_lazy("Sign in confirmation")
    success_url = url_or_reverse(settings.LOGIN_URL)
    tfa_setting_name = 'AUTH_PLUS_USE_EMAIL_TWO_FACTOR_AUTHENTICATION'


class OTPTwoFactorAuthenticateView(TwoFactorAuthMixin, View):
    pass
