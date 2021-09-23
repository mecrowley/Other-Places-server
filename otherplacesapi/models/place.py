from django.db import models


class Place(models.Model):
    """Place Model"""

    opuser = models.ForeignKey("OtherPlacesUser", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    address = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=50)
    created = models.DateTimeField()
    visitors = models.ManyToManyField("OtherPlacesUser", through="VisitedPlace", related_name="visited")
    savers = models.ManyToManyField("OtherPlacesUser", through="SavedPlace", related_name="saved")

    @property
    def isMine(self):
        return self.__isMine

    @isMine.setter
    def isMine(self, value):
        self.__isMine = value

    @property
    def saved(self):
        return self.__saved

    @saved.setter
    def saved(self, value):
        self.__saved = value

    @property
    def visited(self):
        return self.__visited

    @visited.setter
    def visited(self, value):
        self.__visited = value

    @property
    def photos(self):
        return self.__photos

    @photos.setter
    def photos(self, value):
        self.__photos = value
    
    @property
    def totalvisitors(self):
        return self.__totalvisitors

    @totalvisitors.setter
    def totalvisitors(self, value):
        self.__totalvisitors = value
    
    @property
    def totalsaved(self):
        return self.__totalsaved

    @totalsaved.setter
    def totalsaved(self, value):
        self.__totalsaved = value
