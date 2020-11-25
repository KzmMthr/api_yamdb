from django.db import models

from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):

    ROLE_CHOICES = (('admin', 'admin'), ('moderator', 'moderator'), ('user', 'user'))

    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(blank=True)
    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)

    confirmation_code = models.CharField(_('confirmation_code'), max_length=10, null=True, blank=True)

    email = models.EmailField(_('email address'), unique=True, blank=False)

    username = models.CharField(
        max_length=150,
        unique=True,
    )

    objects = CustomUserManager()
