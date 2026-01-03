from typing import Any
from django.core.management.base import BaseCommand
from hrenpack.listwork import tuplist


class DebugBaseCommand(BaseCommand):
    debug_class: Any

    @property
    def debug_init_args(self) -> tuplist:
        return []

    @property
    def debug_init_kwargs(self) -> dict:
        return {}

    @property
    def debug_do_args(self) -> tuplist:
        return []

    @property
    def debug_do_kwargs(self) -> dict:
        return {}

    def handle(self, *args, **options):
        self.kwargs = options
        self.debug_class(*self.debug_init_args, **self.debug_init_kwargs).do(*self.debug_do_args, **self.debug_do_kwargs)
