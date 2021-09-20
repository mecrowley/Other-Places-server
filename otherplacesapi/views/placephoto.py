import uuid
import base64
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from otherplacesapi.models import OtherPlacesUser, Place, PlacePhoto


class PlacePhotoView(ViewSet):
    """Photos of places"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized place photo instance
        """

        placephoto = PlacePhoto()
        placephoto.opuser = OtherPlacesUser.objects.get(user=request.auth.user)
        placephoto.place = Place.objects.get(pk=request.data["placeId"])
        format, imgstr = request.data["photo"].split(';base64,')
        ext = format.split('/')[-1]
        placephoto.photo = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')

        try:
            placephoto.save()
            serializer = PlacePhotoSerializer(placephoto, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)



    def retrieve(self, request, pk=None):
        """Handle GET requests for single place photo

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            placephoto = PlacePhoto.objects.get(pk=pk)
            serializer = PlacePhotoSerializer(placephoto, context={'request': request})
            return Response(serializer.data)
        except PlacePhoto.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)


    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single place photo

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            placephoto = PlacePhoto.objects.get(pk=pk)
            placephoto.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to placephotos resource

        Returns:
            Response -- JSON serialized list of place photos
        """
        placephotos = PlacePhoto.objects.all()

        place = self.request.query_params.get('place', None)
        if place is not None:
            placephotos = placephotos.filter(place__id=place)

        serializer = PlacePhotoSerializer(
            placephotos, many=True, context={'request': request})
        return Response(serializer.data)



class PlacePhotoSerializer(serializers.ModelSerializer):
    """JSON serializer for place photos
    """
    class Meta:
        model = PlacePhoto
        fields = ('id', 'opuser', 'place', 'photo')
