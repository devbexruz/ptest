from django.contrib import admin
from api import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Image)
admin.site.register(models.Test)
admin.site.register(models.Theme)
admin.site.register(models.Ticket)
admin.site.register(models.Variant)

