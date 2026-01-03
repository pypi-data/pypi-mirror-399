import uuid
from hrendjango.debug import BaseDebug
from hrendjango.utils import get_project_name
from .mixins import EmailSendMixin
from .constants import VERIFICATION_CODE_CSS


class PasswordResetDebug(EmailSendMixin, BaseDebug):
    email_template_name = 'auth_plus/email_reset.html'
    subject = "Сброс пароля"
    email_base_context = dict(name="Пользователь", code=123456, reset_url='https://example.com')
    sender_name = get_project_name()
    do_method_name = 'send'

    def get_email_context_data(self, **kwargs) -> dict:
        return super().get_email_context_data(token=uuid.uuid4())
