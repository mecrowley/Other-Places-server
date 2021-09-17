from django.db import models


class PlacePhoto(models.Model):
    """Represents a photo of a place"""
    opuser = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE)
    place = models.ForeignKey("Place", on_delete=models.CASCADE)
    photo = models.ImageField(
        upload_to='placeimages', height_field=None,
        width_field=None, max_length=None, null=True)
    created = models.DateTimeField()