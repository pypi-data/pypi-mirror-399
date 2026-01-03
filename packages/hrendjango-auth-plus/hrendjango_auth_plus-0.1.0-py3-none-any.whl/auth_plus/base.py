from django.contrib.auth import logout, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from hrenpack.framework.django.mixins import SuccessURLMixin
from hrenpack.framework.django.views import View, FormView, LoginView
from .forms import ConfirmCodeForm, LoginForm
from .mixins import ErrorURLMixin, VerificationCodeMixin
from .models import ConfirmationCode

User = get_user_model()


class FormViewPlus(ErrorURLMixin, FormView):
    pass
