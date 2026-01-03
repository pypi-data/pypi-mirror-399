from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy

from hrenpack.boolwork import str_to_bool_soft
from hrenpack.framework.django import url_or_reverse
from hrenpack.framework.django.views import View
from ..base import FormViewPlus
from ..forms import ConfirmCodeForm, SetPasswordFormWithAuthorize
from ..mixins import VerificationCodeMixin, AuthorizeGETParamMixin
from ..models import ConfirmationCode
from .base import User


class PasswordResetRequestView(VerificationCodeMixin, FormViewPlus):
    template_name = 'auth_plus/password_reset/password_reset_form.html'
    email_template_name = 'auth_plus/email/email_reset.html'
    form_class = PasswordResetForm
    title = gettext_lazy("Password reset")
    confirmation_code_type = 'password_reset'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['message'] = self.request.GET.get('message')
        return kwargs

    def form_valid(self, form):
        try:
            self.generate_and_send_verification(User.objects.get(email=form.cleaned_data['email']))
            return redirect(self.get_success_url())
        except User.DoesNotExist:
            form.add_error('email', gettext_lazy("User with this email not found"))
            return self.form_invalid(form)


class PasswordResetCodeVerifyView(FormViewPlus):
    form_class = ConfirmCodeForm
    success_url_root: str
    title = gettext_lazy("Enter the confirmation code")
    template_name = 'auth_plus/password_reset/password_reset_done.html'

    def get(self, request, *args, **kwargs):
        if 'verification_email' not in request.session:
            return redirect(self.get_error_url() + f'?message={gettext_lazy(
                "Session expired, please start resetting your password again")}')
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(self.success_url_root, kwargs={'token': self.request.session['verification_token']})

    def form_valid(self, form):
        email = self.request.session.get('verification_email')
        code = form.cleaned_data['code']

        try:
            confirmation = ConfirmationCode.new.get(
                email=email,
                code=code,
                type='password_reset'
            )

            if confirmation.is_valid():
                self.request.session['verification_token'] = str(confirmation.token)
                return redirect(self.get_success_url())

            form.add_error('code', gettext_lazy("The code has expired"))
        except ConfirmationCode.DoesNotExist:
            form.add_error('code', gettext_lazy("Invalid verification code"))
        return self.form_invalid(form)


class PasswordResetConfirmView(AuthorizeGETParamMixin, FormViewPlus):
    form_class = SetPasswordFormWithAuthorize
    title = gettext_lazy("Create a new password")
    template_name = 'auth_plus/password_reset/password_reset_confirm.html'

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            user = User.objects.get(email=self.request.session['verification_email'])
        except (User.DoesNotExist, KeyError):
            raise Http404(gettext_lazy("User does not exist"))
        else:
            kwargs['user'] = user
            return kwargs

    def get(self, request, token=None, *args, **kwargs):
        if token:
            try:
                confirmation = ConfirmationCode.new.get(
                    token=token,
                    type='password_reset'
                )

                try:
                    user = User.objects.get(email=confirmation.email)
                except User.DoesNotExist:
                    raise Http404(gettext_lazy("User with this email not found"))

                if confirmation.is_valid():
                    request.session['verification_email'] = confirmation.email
                    request.session['verification_token'] = str(token)
                    return super().get(request, *args, **kwargs)
                else:
                    raise Http404(gettext_lazy("The code has already been used or has expired"))
            except ConfirmationCode.DoesNotExist:
                raise Http404(gettext_lazy("Invalid verification code"))

        # Обработка после ввода кода
        if 'verification_token' not in request.session:
            return redirect(self.get_error_url())

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        email = self.request.session.get('verification_email')
        token = self.request.session.get('verification_token')
        new_password = form.cleaned_data['new_password1']
        self.authorize = form.cleaned_data['authorize']

        try:
            if token:
                confirmation = ConfirmationCode.new.get(
                    token=token,
                    type='password_reset'
                )

                if confirmation.is_valid() and confirmation.email == email:
                    user = User.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()

                    confirmation.is_used = True
                    confirmation.save()

                    # Очищаем сессию
                    if 'reset_token' in self.request.session:
                        del self.request.session['verification_token']

                    return redirect(self.get_success_url())
        except User.DoesNotExist:
            pass
        except ConfirmationCode.DoesNotExist:
            raise Http404

        return redirect(self.get_error_url() + f'?message={gettext_lazy("Password reset error")}')

    def get_success_url(self):
        return self.success_url + f'?{self.GET_param_name}={str(self.authorize).lower()}'


class PasswordResetCompleteView(AuthorizeGETParamMixin, View):
    title = gettext_lazy("Password is changed")
    login_url: str = url_or_reverse(settings.LOGIN_URL)
    template_name = 'auth_plus/password_reset/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(login_url=self.login_url, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.GET_param_name:
            self.authorize = str_to_bool_soft(request.GET.get(self.GET_param_name, False), True)
        if self.authorize:
            try:
                login(request, User.objects.get(email=self.request.session['verification_email']))
            except User.DoesNotExist:
                raise Http404("User does not exist")
            else:
                if 'reset_email' in self.request.session:
                    del self.request.session['verification_email']

        return render(request, self.template_name, self.get_context_data())