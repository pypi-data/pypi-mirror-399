from auth_plus.debug import PasswordResetDebug
from auth_plus.management.base import DebugBaseCommand
from hrenpack.listwork import tuplist


class Command(DebugBaseCommand):
    debug_class = PasswordResetDebug

    @property
    def debug_do_args(self) -> tuplist:
        return [self.kwargs['email']]

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+', type=str)
