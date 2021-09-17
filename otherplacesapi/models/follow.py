from django.db import models

class Follow(models.Model):
    """Join model for User Follows
    """
    follower = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE, related_name="follower")
    opuser = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE, related_name="opuser")
