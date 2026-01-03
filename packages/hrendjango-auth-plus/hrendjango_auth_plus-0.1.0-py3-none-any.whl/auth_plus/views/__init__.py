from django.conf import settings
from django.contrib.auth import logout, update_session_auth_hash
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy
from hrenpack.framework.django import url_or_reverse, view_dict
from hrenpack.framework.django.views import RegistrationView as HrenpackRegistrationView
from .. import TFA_WAYS
from ..forms import RegistrationForm, UserProfileForm
from .base import *
from .password_reset import *
from .tfa import *
from .verify_email import *


class LoginView(BaseLoginView):
    pass


class TwoFactorAuthenticationLoginView(BaseLoginView):
    def form_valid(self, form):
        """Сохраняет username в сессию и выходит из аккаунта."""
        response = super().form_valid(form)
        user = self.request.user
        self.request.session['user_id'] = user.pk
        logout(self.request)
        return redirect(self.get_success_url())

    def get_success_url(self, user=None):
        if user:
            for way in TFA_WAYS:
                if way.tfa_user_enabled(user):
                    return url_or_reverse(way.url)
        return super().get_success_url()


class RegistrationView(HrenpackRegistrationView):
    form_class = RegistrationForm
    success_url = url_or_reverse(settings.LOGIN_URL)


class EditProfileView(SuccessURLMixin, View, LoginRequiredMixin):
    title = gettext_lazy("Change user settings")
    form_class = UserProfileForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, view_dict(self.title, self.h1_title, form=form))

    def post(self, request, *args, **kwargs):
        user = request.user
        form = self.form_class(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Обновляем профиль пользователя
            form.save()

            # Обработка изменения пароля
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password')

            if old_password and new_password:
                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Обновляем сессию
                else:
                    form.add_error('old_password', gettext_lazy("Old password is incorrect"))

            # messages.success(request, "Профиль успешно обновлен.")
            return redirect(self.get_success_url())
        return render(request, self.template_name, self.get_context_data(form=form))



