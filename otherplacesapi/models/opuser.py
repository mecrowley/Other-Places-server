from django.db import models
from django.contrib.auth.models import User


class OtherPlacesUser(models.Model):
    """Represents a user of the Other Places application"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255)
    profile_pic = models.ImageField(
        upload_to='profileimages', height_field=None,
        width_field=None, max_length=None, null=True)

    @property
    def isMe(self):
        return self.__isMe

    @isMe.setter
    def isMe(self, value):
        self.__isMe = value
