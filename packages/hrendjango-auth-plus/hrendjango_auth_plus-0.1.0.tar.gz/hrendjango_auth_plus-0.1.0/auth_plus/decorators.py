import functools
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from hrendjango.exceptions import Http401


def auth_required(arg=None):
    def decorator(view_function):
        @functools.wraps(view_function)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if arg is None:
                    raise Http401
                elif isinstance(arg, HttpResponse):
                    arg.status_code = 401
                    return arg
                elif isinstance(arg, (str, bytes, bytearray)):
                    try:
                        html = render_to_string(arg)
                    except TemplateDoesNotExist:
                        html = arg
                    return HttpResponse(html, status=401)
                elif isinstance(arg, dict):
                    return JsonResponse(arg)
                else:
                    raise TypeError('Argument must be either a string or a HttpResponse')
            return view_function(request, *args, **kwargs)
        return wrapper
    return decorator


def verified_email_required(func):
    lr_func = login_required(func)

    @functools.wraps(lr_func)
    def wrapper(request, *args, **kwargs):
        if request.user.email_verified:
            return lr_func(request, *args, **kwargs)
        return redirect(reverse_lazy(settings.AUTH_PLUS_EMAIL_VERIFICATION_URL))
    return wrapper
