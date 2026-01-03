from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import FieldError
from django.utils.translation import gettext_lazy
from .mixins import ProfileMixin, RecaptchaMixin
from .models import ConfirmationCode
from .__forms__test__ import *


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=gettext_lazy("Username or email"),
                               widget=forms.TextInput())
    password = forms.CharField(label=gettext_lazy("Password"), widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')


class RegistrationForm(UserCreationForm, ProfileMixin):
    username = forms.CharField(label=gettext_lazy("Username"))
    password1 = forms.CharField(label=gettext_lazy("Password"), widget=forms.PasswordInput())
    password2 = forms.CharField(label=gettext_lazy("Password confirmation"), widget=forms.PasswordInput())

    class Meta(ProfileMixin.Meta):
        fields = ('avatar', 'username', 'email', 'first_name', 'last_name',
                  'password1', 'password2', 'birth_date', 'gender')

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError(gettext_lazy("An account with this email already exists"))
        return email

try:
    class RegistrationFormWithReCaptcha(RecaptchaMixin, RegistrationForm):
        class Meta(RegistrationForm.Meta):
            fields = ('avatar', 'username', 'email', 'first_name', 'last_name',
                      'password1', 'password2', 'birth_date', 'gender', 'captcha')
except FieldError:
    pass


class UserProfileForm(ProfileMixin):
    old_password = forms.CharField(label=gettext_lazy("Old password"), widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(label=gettext_lazy("New password"), widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(label=gettext_lazy("Password confirmation"), widget=forms.PasswordInput, required=False)

    class Meta(ProfileMixin.Meta):
        fields = ('avatar', 'username', 'email', 'first_name', 'last_name',
                  'old_password', 'new_password', 'confirm_password', 'birth_date', 'gender')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', gettext_lazy("The passwords do not match"))

        return cleaned_data


class ConfirmCodeForm(forms.Form):
    code = forms.CharField(label=gettext_lazy("Verification code"))


class SetPasswordFormWithAuthorize(SetPasswordForm):
    authorize = forms.BooleanField(initial=True, label=gettext_lazy("Log in after resetting your password"))


class SetPasswordFormWithRecaptchaAndAuthorize(RecaptchaMixin, SetPasswordFormWithAuthorize):
    pass


class OTPAuthenticationForm(forms.Form):
    otp_token = forms.CharField(
        label=gettext_lazy(gettext_lazy("Verification code")),
        max_length=6,
        required=False,
        widget=forms.TextInput(attrs=dict(autocomplete='off'))
    )
