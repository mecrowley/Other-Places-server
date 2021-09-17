from django.db import models


class Comment(models.Model):
    """Comment model"""
    opuser = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE)
    place = models.ForeignKey("Place", on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField()