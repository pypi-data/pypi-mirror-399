from hrenpack.strwork import randstr

__all__ = ['generate_confirmation_code']


def generate_confirmation_code():
    return randstr(100000, 999999)
