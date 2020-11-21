from django.db import models

from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=100)

    email = models.EmailField(_('email address'), unique=True, blank=False)

    username = models.CharField(
        max_length=150,
        unique=True,
    )

    objects = CustomUserManager()
