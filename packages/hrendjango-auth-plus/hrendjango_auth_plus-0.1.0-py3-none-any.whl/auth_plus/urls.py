from django.urls import path, register_converter
from . import views
from .converters import TwoFactorAuthenticationConverter

app_name = 'auth_plus'
register_converter(TwoFactorAuthenticationConverter, 'tfa')

urlpatterns = [
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('verify-email/<uuid:token>/', views.VerifyEmailCompleteView.as_view(), name='verify_email_complete'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetCodeVerifyView.as_view(), name='password_reset_done'),
    path('password-reset/<uuid:token>/', views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('two-factor/email/', views.EmailTwoFactorAuthenticateView.as_view(), name='two_factor_email'),
]
