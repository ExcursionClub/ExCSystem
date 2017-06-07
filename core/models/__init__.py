from django.db import models

from django.contrib.auth.models import AbstractUser

# Member must be in the __init__.py file so django can import it directly from the models module

class Member(AbstractUser):


    pass