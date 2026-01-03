from django.db.models import Manager

__all__ = ['NotUsedManager']


class NotUsedManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_used=False)
