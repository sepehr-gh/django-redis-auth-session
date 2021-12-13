import binascii
import os
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(max_length=40, primary_key=True, unique=True)
    refresh = models.CharField(max_length=80, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        abstract = False
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    @classmethod
    def generate_refresh(cls):
        return binascii.hexlify(os.urandom(40)).decode()

    def save(self, *args, **kwargs):
        if not self.refresh:
            self.refresh = self.generate_refresh()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.key
