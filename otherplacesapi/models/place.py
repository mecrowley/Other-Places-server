from django.db import models


class Place(models.Model):
    """Place Model"""

    opuser = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    address = models.CharField(max_length=100)
    created = models.DateTimeField()
