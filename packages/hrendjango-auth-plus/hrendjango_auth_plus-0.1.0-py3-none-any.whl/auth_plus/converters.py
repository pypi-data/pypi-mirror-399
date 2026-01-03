from hrendjango.converters import BaseLiteralStringConverter
from hrenpack.listwork import strlist
from . import TFA_WAYS


class TwoFactorAuthenticationConverter(BaseLiteralStringConverter):
    allowed = strlist(TFA_WAYS)
