from django.db import models
from django.contrib.auth.models import User

class PrivateNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret_content = models.CharField(max_length=255)