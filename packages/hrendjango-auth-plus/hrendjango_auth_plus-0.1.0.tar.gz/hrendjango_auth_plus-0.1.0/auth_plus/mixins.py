import uuid, warnings
from typing import Optional
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import Http404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import classonlymethod, method_decorator
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from hrenpack.framework.django.mixins import UserAuthorizeMixin
from hrenpack.listwork import merging_dictionaries, get_from_dict
from hrenpack.encapsulation import set_attrs_if_is_none
from .constants import VERIFICATION_CODE_CSS
from .decorators import auth_required, verified_email_required
from .models import ConfirmationCode
from .utils import get_default_signature, get_project_name
from .tfa_ways import TwoFactorAuthenticationWay


class EmailSendMixin:
    email_template_name: str
    email_extra_context: dict = {}
    subject: Optional[str]
    signature: str = get_default_signature()
    sender_email: str = settings.DEFAULT_FROM_EMAIL
    sender_name: Optional[str] = get_project_name()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.subject = self.title

    def get_email_context_data(self, **kwargs) -> dict:
        kwargs.update(self.email_extra_context)
        return kwargs

    def email_render(self):
        body_html = render_to_string(self.email_template_name, self.get_email_context_data()).strip()
        return mark_safe(body_html)

    def send(self, to_email: list):
        html = self.email_render()
        from_email = f'{self.sender_name} <{self.sender_email}>' if self.sender_name is None else self.sender_email
        send_mail(self.subject, strip_tags(html), from_email, to_email, html_message=html)

    @classonlymethod
    def as_view(cls, **initkwargs):
        set_attrs_if_is_none(get_from_dict(initkwargs, 'email_template_name', 'email_extra_context', 'subject',
                                           pop_mode=True))
        return super().as_view(**initkwargs)


class VerificationCodeMixin(EmailSendMixin):
    email_base_context: dict = {}
    code_style: str = VERIFICATION_CODE_CSS
    confirm_url_root: str
    confirmation_code_type: str

    def get_email_context_data(self, **kwargs) -> dict:
        kwargs = merging_dictionaries(kwargs, self.email_base_context, self.email_extra_context)
        kwargs.update(subject=self.subject, signature=self.signature, code_style=self.code_style)
        return kwargs

    def generate_and_send_verification(self, user):
        email = user.email
        confirmation = ConfirmationCode.objects.create(email=email, type=self.confirmation_code_type)
        token = confirmation.token
        reset_url = self.request.build_absolute_uri(reverse_lazy(self.confirm_url_root, kwargs=dict(token=token)))
        self.email_base_context = dict(code=confirmation.code, email=email, reset_url=reset_url,
                                       reset_user=user, name=user.get_full_name())
        self.send([email])
        self.request.session['verification_email'] = email
        self.request.session['verification_token'] = str(token)


class AuthorizeGETParamMixin(UserAuthorizeMixin):
    GET_param_name: Optional[str] = 'authorize'

    @classonlymethod
    def as_view(cls, **initkwargs):
        if 'GET_param_name' in initkwargs:
            cls.GET_param_name = initkwargs.pop('GET_param_name', None)
        return super().as_view(**initkwargs)


class ErrorURLMixin:
    error_url: str

    def get_error_url(self):
        return self.error_url


@method_decorator(verified_email_required, 'dispatch')
class VerifiedEmailRequiredMixin(LoginRequiredMixin):
    pass


class TwoFactorAuthMixin:
    tfa_way: TwoFactorAuthenticationWay

    def get(self, request, *args, **kwargs):
        if not getattr(settings, self.tfa_way.enable_setting_name, False):
            raise Http404
        return super().get(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     return super().post()(request, *args, **kwargs)


class ProfileMixin(forms.ModelForm):
    avatar = forms.ImageField(required=False, widget=forms.FileInput(), label="Фото профиля")
    birth_date = forms.DateField(label="Дата рождения", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    gender = forms.ChoiceField(label="Пол", widget=forms.Select, required=False,
                               choices=(["Мужской"] * 2, ["Женский"] * 2, ["Другой"] * 2, ["Не указан"] * 2))

    class Meta:
        fields = ('avatar', 'username', 'email', 'first_name', 'last_name', 'birth_date', 'gender')
        model = get_user_model()
        labels = dict(
            email="Адрес электронной почты",
            first_name="Имя",
            last_name="Фамилия"
        )

try:
    from django_recaptcha.fields import ReCaptchaField, ReCaptchaV2Checkbox
except ImportError:
    class RecaptchaMixin:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError("Recaptcha is not installed")
else:
    class RecaptchaMixin:
        captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
