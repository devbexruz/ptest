from django.db import models

class RoleChoices(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    STUDENT = 'STUDENT', 'Student'

class TestChoices(models.TextChoices):
    EXAM = 'EXAM', "Exam"
    TICKET = 'TICKET', "Ticket"
    SETTEST = "SETTEST", "Settest"

