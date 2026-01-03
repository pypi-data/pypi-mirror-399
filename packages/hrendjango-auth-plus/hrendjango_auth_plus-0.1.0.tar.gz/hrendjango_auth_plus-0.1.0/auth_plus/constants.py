from django.conf import settings
from hrenpack.framework.django import get_app_inclusion_namespace
from .tfa_ways import TwoFactorAuthenticationWays, TwoFactorAuthenticationWay
from .shortcuts import auth_plus_urls_namespace

auth_plus_url = lambda url: auth_plus_urls_namespace() + ':' + url

AUTH_PLUS_TEMPLATES_DIR = getattr(settings, 'AUTH_PLUS_TEMPLATES_DIR', '')
AUTH_PLUS_EMAIL_VERIFICATION_CODE_PERIOD = getattr(settings, 'AUTH_PLUS_EMAIL_VERIFICATION_CODE_PERIOD', 600)

CONFIRMATION_CODE_TYPE_SUBJECTS = dict(
    email_verification="Подтверждение email",
    password_reset="Сброс пароля"
)

VERIFICATION_CODE_CSS = """
    margin: 0 45%;
    width: 10%;
    padding: 5px;
    background: #c000c0;
    color: #ededed;
    text-align: center;
    border-radius: 20px;
    font-weight: bold;
    font-size: 16pt;
"""

DEFAULT_EMAIL_TWO_FACTOR_AUTHENTICATION_URL = auth_plus_url('two_factor_email')
DEFAULT_OTP_TWO_FACTOR_AUTHENTICATION_URL = auth_plus_url('two_factor_otp')
DEFAULT_RECOVERY_CODE_TWO_FACTOR_AUTHENTICATION_URL = auth_plus_url('two_factor_recovery_code')

EMAIL_TFA_WAY = TwoFactorAuthenticationWay('email', "AUTH_PLUS_USE_EMAIL_TWO_FACTOR_AUTHENTICATION",
                                           "AUTH_PLUS_EMAIL_TWO_FACTOR_AUTHENTICATION_URL",
                                           DEFAULT_EMAIL_TWO_FACTOR_AUTHENTICATION_URL, "Код подтверждения Email",
                                           'tfa_email_enabled')
OTP_TFA_WAY = TwoFactorAuthenticationWay('otp', "AUTH_PLUS_USE_OTP_TWO_FACTOR_AUTHENTICATION",
                                         "AUTH_PLUS_OTP_TWO_FACTOR_AUTHENTICATION_URL",
                                         DEFAULT_OTP_TWO_FACTOR_AUTHENTICATION_URL, "Код подтверждения OTP",
                                         'tfa_otp_enabled')
RECOVERY_CODE_TFA_WAY = TwoFactorAuthenticationWay('recovery-code',
                                                   "AUTH_PLUS_USE_RECOVERY_CODE_TWO_FACTOR_AUTHENTICATION",
                                                   "AUTH_PLUS_RECOVERY_CODE_TWO_FACTOR_AUTHENTICATION_URL",
                                                   DEFAULT_RECOVERY_CODE_TWO_FACTOR_AUTHENTICATION_URL,
                                                   "Код восстановления", 'tfa_recovery_code_enabled')

DEFAULT_TFA_WAYS = TwoFactorAuthenticationWays(EMAIL_TFA_WAY, OTP_TFA_WAY, RECOVERY_CODE_TFA_WAY)
