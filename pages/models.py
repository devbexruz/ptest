from django.db import models
from django.contrib.auth.models import AbstractUser

class RoleChoices(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    USER = 'STUDENT', 'Student'


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
    )
    ruxsat = models.BooleanField(default=False)

class Test(models.Model):
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.title

