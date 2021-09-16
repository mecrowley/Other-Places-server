from django.db import models
from django.contrib.auth.models import User


class OtherPlacesUser(models.Model):
    """Represents a user of the Other Places application"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255)
