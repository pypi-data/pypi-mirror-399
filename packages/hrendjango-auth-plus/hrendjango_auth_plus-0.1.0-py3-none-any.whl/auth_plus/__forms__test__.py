from django.conf import settings
from django.utils.translation import gettext_lazy

*package, auth_backend = settings.AUTHENTICATION_BACKENDS[0].split('.')
package = '.'.join(package)

if package != 'auth_plus.backends':
    raise ValueError

match auth_backend:
    case 'UsernameBackend':
        is_combine = False
        label = gettext_lazy("Username")
    case 'EmailBackend':
        is_combine = False
        label = gettext_lazy("Email")
    case 'CombinedBackend':
        is_combine = True
        label = f'{gettext_lazy("Username")} {gettext_lazy("or")} {gettext_lazy("Email")}'
    case _:
        raise ValueError(f'Auth backend {auth_backend} not supported')

label = str(label)

if is_combine:
    label = label[0].upper() + label[1:].lower()
