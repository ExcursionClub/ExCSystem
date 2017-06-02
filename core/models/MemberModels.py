from django.db import models

from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractBaseUser


class Member(AbstractBaseUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']