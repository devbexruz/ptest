from django.db import models

class RoleChoices(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    STUDENT = 'STUDENT', 'Student'
