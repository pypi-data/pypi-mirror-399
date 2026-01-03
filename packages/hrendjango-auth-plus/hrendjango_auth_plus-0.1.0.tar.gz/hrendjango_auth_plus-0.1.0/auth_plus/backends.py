from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.db.models import Q
from django.forms import ValidationError

__all__ = ['UsernameBackend', 'EmailBackend', 'CombinedBackend']

UserModel = get_user_model()


class UsernameBackend(ModelBackend):
    pass


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
            return None
        except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
            return None


class CombinedBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
            return None
        except UserModel.DoesNotExist:
            raise ValidationError("Пользователя не существует")
        except UserModel.MultipleObjectsReturned:
            return None
