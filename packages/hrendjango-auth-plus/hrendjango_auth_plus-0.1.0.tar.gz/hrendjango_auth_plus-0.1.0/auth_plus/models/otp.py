import pyotp, qrcode, qrcode.image.svg, io
from datetime import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy

from hrendjango.utils import get_project_name, safe_get_user_model


class UserOTP(models.Model):
    user = models.OneToOneField(safe_get_user_model(), on_delete=models.CASCADE, verbose_name=gettext_lazy('User'))
    totp_secret = models.CharField(max_length=120)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()

    def get_totp_uri(self):
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(self.user.email, get_project_name())

    def verify_token(self, token):
        totp = pyotp.TOTP(self.totp_secret)
        is_valid = totp.verify(token)
        if is_valid:
            self.last_used = timezone.now()
            self.save()
        return is_valid

    def generate_token(self):
        return pyotp.totp.TOTP(self.totp_secret).now()

    def generate_qr_code(self):
        uri = self.get_totp_uri()
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(uri, image_factory=factory, box_size=10)
        stream = io.BytesIO()
        img.save(stream)
        return stream.getvalue().decode()

