from django.utils.deprecation import MiddlewareMixin
from . import TFA_WAYS


class AuthPlusMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.TFA_WAYS = TFA_WAYS
