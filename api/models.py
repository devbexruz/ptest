from django.db import models
from django.contrib.auth.models import AbstractUser
from . import enums
import uuid, os

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
    correct_answer = models.ForeignKey(
        "api.Variant",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='true_tests'
    )

    image = models.ImageField(upload_to='images/', null=True, blank=True)
    active = models.BooleanField(default=False)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        """
        Model o'chirilganda faylni ham o'chiradi
        """
        if self.image:
            # Fayl yo'lini saqlab olamiz
            storage, path = self.image.storage, self.image.path
            # Super methodni chaqiramiz (model o'chiriladi)
            super().delete(*args, **kwargs)
            # Faylni o'chiramiz
            storage.delete(path)
        else:
            super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Yangi rasm yuklanganda eski rasmni o'chiradi
        """
        if self.pk:
            try:
                old_instance = Test.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    if os.path.isfile(old_instance.image.path):
                        os.remove(old_instance.image.path)
            except Test.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    def __str__(self):
        return self.value

class Variant(models.Model):
    value = models.TextField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
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
        choices=enums.TestChoices.choices,
        default=enums.TestChoices.EXAM
    )
    finished = models.BooleanField(default=False)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} - {self.test_type} - {'Correct' if self.is_correct else 'Incorrect'}"

class TestSheet(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    current_answer = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True)
    selected = models.BooleanField(default=False)
    successful = models.BooleanField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.result.id} - {'Successful' if self.successful else 'Unsuccessful'}"

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_token')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)  # user-agent
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} -> {self.token}"

