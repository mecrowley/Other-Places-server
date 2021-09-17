"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.contrib.auth.models import User
from otherplacesapi.models import OtherPlacesUser, Place
import datetime


class PlaceView(ViewSet):
    """Other Places places"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized place instance
        """
        place = Place()
        place.opuser = OtherPlacesUser.objects.get(user=request.auth.user)
        place.title = request.data["title"]
        place.description = request.data["description"]
        place.address = request.data["address"]
        place.created = datetime.datetime.now()

        try:
            place.save()
            serializer = PlaceSerializer(place, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)



    def retrieve(self, request, pk=None):
        """Handle GET requests for single place

        Returns:
            Response -- JSON serialized place instance
        """
        try:
            place = Place.objects.get(pk=pk)
            serializer = PlaceSerializer(place, context={'request': request})
            return Response(serializer.data)
        except Place.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a place

        Returns:
            Response -- Empty body with 204 status code
        """
        place = Place.objects.get(pk=pk)
        place.title = request.data["title"]
        place.description = request.data["description"]
        place.address = request.data["address"]
        place.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single place

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            place = Place.objects.get(pk=pk)
            place.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to places resource

        Returns:
            Response -- JSON serialized list of places
        """
        places = Place.objects.all()

        opuser = self.request.query_params.get('user', None)
        if opuser is not None:
            places = places.filter(opuser__id=opuser)

        serializer = PlaceSerializer(
            places, many=True, context={'request': request})
        return Response(serializer.data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'date_joined')


class OtherPlacesUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    class Meta:
        model = OtherPlacesUser
        fields = ('id', 'user')


class PlaceSerializer(serializers.ModelSerializer):
    opuser = OtherPlacesUserSerializer
    class Meta:
        model = Place
        fields = ('id', 'opuser', 'title', 'description', 'address', 'created')
