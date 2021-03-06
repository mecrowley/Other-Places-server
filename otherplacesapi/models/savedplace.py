from django.db import models


class SavedPlace(models.Model):
    """Model for User's favorite place"""
    opuser = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE)
    place = models.ForeignKey("Place", on_delete=models.CASCADE)
