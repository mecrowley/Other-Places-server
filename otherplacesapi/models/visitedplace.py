from django.db import models


class VisitedPlace(models.Model):
    """Model for User's visited place"""
    opuser = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE)
    place = models.ForeignKey("Place", on_delete=models.CASCADE)
