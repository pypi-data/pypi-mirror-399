from django.contrib.auth import logout, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy
from hrenpack.framework.django.mixins import SuccessURLMixin
from hrenpack.framework.django.views import View, LoginView
from ..forms import ConfirmCodeForm, LoginForm
from ..mixins import ErrorURLMixin, VerificationCodeMixin
from ..models import ConfirmationCode

User = get_user_model()


class BaseSendAndVerifyView(SuccessURLMixin, ErrorURLMixin, LoginRequiredMixin, VerificationCodeMixin, View):
    error_url = 'index'
    form_class = ConfirmCodeForm
    title = gettext_lazy("Enter the confirmation code")

    def get_success_url(self):
        return reverse(self.confirm_url_root, kwargs={'token': self.request.session['reset_token']})

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.email_verified:
            logout(request)
            self.generate_and_send_verification(user)
            form = self.form_class()
            return render(request, self.template_name, self.get_context_data(form=form))
        return redirect(self.get_error_url())

    def post(self, request, *args, **kwargs):
        user = request.user
        code = request.POST.get('code')
        email = user.email

        confirmation = ConfirmationCode.new.filter(email=email, code=code, type='email_verification').first()

        if not confirmation or not confirmation.is_valid() or confirmation.code != code:
            raise ValidationError(gettext_lazy("Invalid or outdated verification code"))

        confirmation.is_used = True
        confirmation.save()

        return redirect(self.get_success_url())


class BaseSendAndVerifyCompleteView(View):
    session_expired_url: str
    email_already_url: str
    dont_header = True

    def get(self, request, token, *args, **kwargs):
        try:
            user = User.objects.get(email=request.session['verification_email'])
            login(request, user)
            if not user.email_verified:
                user.email_verified = True
                user.save()
                return render(request, self.template_name, self.get_context_data())
            return redirect(self.get_email_already_url())
        except KeyError:
            return redirect(self.get_session_expired_url())

    def get_session_expired_url(self):
        return self.session_expired_url

    def get_email_already_url(self):
        return self.email_already_url


class BaseLoginView(LoginView):
    form_class = LoginForm
