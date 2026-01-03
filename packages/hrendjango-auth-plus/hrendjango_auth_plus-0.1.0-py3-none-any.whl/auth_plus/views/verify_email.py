from django.utils.translation import gettext_lazy
from hrenpack.framework.django.views import View
from .base import BaseSendAndVerifyView


class VerifyEmailView(BaseSendAndVerifyView):
    email_template_name = 'auth_plus/email/email_verification.html'
    confirmation_code_type = 'email_verification'
    title = gettext_lazy("Email confirmation")
    template_name = 'auth_plus/verification_code/email_verification_code.html'


class VerifyEmailCompleteView(View):
    template_name = 'auth_plus/verify_email_complete.html'
    title = gettext_lazy("Email verified")
