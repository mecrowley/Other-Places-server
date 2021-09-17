from django.db import models


class ListPlace(models.Model):
    """Join model for place on a list"""
    list = models.ForeignKey("List", on_delete=models.CASCADE)
    place = models.ForeignKey("Place", on_delete=models.CASCADE)
