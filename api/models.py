from django.db import models
from django.contrib.auth.models import AbstractUser
from . import enums
# Create your models here.

class User(AbstractUser):
    full_name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=20,
        choices=enums.RoleChoices.choices,
        default=enums.RoleChoices.STUDENT,
    )
    ruxsat = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Image(models.Model):
    image = models.ImageField(upload_to='media/images/')

    def __str__(self):
        return self.image.url
class Theme(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Ticket(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Test(models.Model):
    value = models.TextField()
    correct_answer = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)

    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    def __str__(self):
        return self.value

class Variant(models.Model):
    value = models.TextField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.value

class Result(models.Model):
    # Userning natijalari
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Kerakli numberlar
    test_length = models.IntegerField()
    true_answers = models.IntegerField()

    # test ni qaysi turda yechgan
    test_type = models.CharField(
        max_length=100,
        choices=enums.TestTypeChoices.choices,
        default=enums.TestTypeChoices.EXAM
    )
    start_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.test_type} - {'Correct' if self.is_correct else 'Incorrect'}"

class TestAnswerSheet(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    current_answer = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.result.id} - {'Successful' if self.successful else 'Unsuccessful'}"
