from django.db import models


class List(models.Model):
    """List model"""
    opuser = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE)
    created = models.DateTimeField()
