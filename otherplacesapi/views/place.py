"""View module for handling requests about games"""
import uuid
import base64
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from django.http import HttpResponseServerError
from django.db.models import Q
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from otherplacesapi.models import OtherPlacesUser, Place, PlacePhoto, VisitedPlace, SavedPlace, Follow
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
        place.city = request.data["city"]
        place.state = request.data["state"]
        place.postal_code = request.data["postal_code"]
        place.country = request.data["country"]
        place.created = datetime.datetime.now()
        place.save()

        if len(request.data["photos"]) > 0:
            placephotos = request.data["photos"]
            for placephoto in placephotos:
                photo = PlacePhoto()
                photo.opuser = OtherPlacesUser.objects.get(user=request.auth.user)
                photo.place = Place.objects.get(pk=place.id)
                format, imgstr = placephoto.split(';base64,')
                ext = format.split('/')[-1]
                photo.photo = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                photo.created = datetime.datetime.now()
                photo.save()
        else:
            pass

        try:
            serializer = PlaceSerializer(place, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)



    def retrieve(self, request, pk=None):
        """Handle GET requests for single place

        Returns:
            Response -- JSON serialized place instance
        """
        authuser = OtherPlacesUser.objects.get(user=request.auth.user)
        try:
            place = Place.objects.get(pk=pk)

            photos = PlacePhoto.objects.filter(place=place)
            photo_list = PlacePhotoSerializer(
                photos, many=True, context={'request': request})
            place.photos = photo_list.data
            place.visited = authuser in place.visitors.all()
            place.saved = authuser in place.savers.all()
            place.totalvisitors = len(VisitedPlace.objects.filter(place=place))
            place.totalsaved = len(SavedPlace.objects.filter(place=place))

            if authuser == place.opuser:
                place.isMine = True
            else:
                place.isMine = False
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
        place.city = request.data["city"]
        place.state = request.data["state"]
        place.postal_code = request.data["postal_code"]
        place.country = request.data["country"]
        place.save()

        if len(request.data["deletedPhotos"]) > 0:
            deletedphotos = request.data["deletedPhotos"]
            for deletedphoto in deletedphotos:
                delete = PlacePhoto.objects.get(pk=deletedphoto["id"])
                delete.delete()

        if len(request.data["photos"]) > 0:
            placephotos = request.data["photos"]
            for placephoto in placephotos:
                photo = PlacePhoto()
                photo.opuser = OtherPlacesUser.objects.get(user=request.auth.user)
                photo.place = Place.objects.get(pk=pk)
                format, imgstr = placephoto.split(';base64,')
                ext = format.split('/')[-1]
                photo.photo = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                photo.created = datetime.datetime.now()
                photo.save()
        else:
            pass

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
        authuser = OtherPlacesUser.objects.get(user=request.auth.user)
        places = Place.objects.all()
        
        for place in places:
            photos = PlacePhoto.objects.filter(place=place)
            photo_list = PlacePhotoSerializer(
                photos, many=True, context={'request': request})
            place.photos = photo_list.data

        for place in places:
            place.saved = authuser in place.savers.all()

        for place in places:
            place.visited = authuser in place.visitors.all()

        for place in places:
            if authuser == place.opuser:
                place.isMine = True
            else:
                place.isMine = False

        for place in places:
            place.totalvisitors = len(VisitedPlace.objects.filter(place=place))
        
        for place in places:
            place.totalsaved = len(SavedPlace.objects.filter(place=place))

        opuser = self.request.query_params.get('userauthor', None)
        if opuser is not None:
            places = places.filter(opuser__id=opuser)


        serializer = PlaceSerializer(
            places, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def saveplace(self, request, pk=None):
        """Managing users saving a place"""
        opuser = OtherPlacesUser.objects.get(user=request.auth.user)
        place = None
        try:
            place = Place.objects.get(pk=pk)
        except Place.DoesNotExist:
            return Response(
                {'message': 'Place does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == "POST":
            try:
                place.savers.add(opuser)
                return Response({}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({'message': ex.args[0]})

        elif request.method == "DELETE":
            try:
                place.savers.remove(opuser)
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]})
    
    
    @action(methods=['post', 'delete'], detail=True)
    def visitplace(self, request, pk=None):
        """Managing users visiting a place"""
        opuser = OtherPlacesUser.objects.get(user=request.auth.user)
        place = None
        try:
            place = Place.objects.get(pk=pk)
        except Place.DoesNotExist:
            return Response(
                {'message': 'Place does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == "POST":
            try:
                place.visitors.add(opuser)
                return Response({}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({'message': ex.args[0]})

        elif request.method == "DELETE":
            try:
                place.visitors.remove(opuser)
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]})
    
    
    @action(methods=['get'], detail=False)
    def following(self, request, pk=None):
        """Managing users visiting a place"""
        opuser = OtherPlacesUser.objects.get(user=request.auth.user)
        follows = Follow.objects.filter(follower=opuser)
        opuserposts = Place.objects.filter(opuser=opuser)
        if len(follows) > 0 and len(opuserposts) > 0:
            for follow in follows:
                places = Place.objects.filter(Q(opuser=follow.opuser) | Q(opuser=opuser))
        elif len(follows) > 0:
            for follow in follows:
                places = Place.objects.filter(opuser=follow.opuser)
        elif len(opuserposts) > 0:
            places = opuserposts
        else:
            places = None

        if places == None:
            return Response([])
        else:
            for place in places:
                photos = PlacePhoto.objects.filter(place=place)
                photo_list = PlacePhotoSerializer(
                    photos, many=True, context={'request': request})
                place.photos = photo_list.data

            for place in places:
                place.saved = opuser in place.savers.all()

            for place in places:
                place.visited = opuser in place.visitors.all()

            for place in places:
                if opuser == place.opuser:
                    place.isMine = True
                else:
                    place.isMine = False

            for place in places:
                place.totalvisitors = len(VisitedPlace.objects.filter(place=place))
            
            for place in places:
                place.totalsaved = len(SavedPlace.objects.filter(place=place))

            serializer = PlaceSerializer(
                places, many=True, context={'request': request})
            return Response(serializer.data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'username')


class OtherPlacesUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    class Meta:
        model = OtherPlacesUser
        fields = ('id', 'user')


class PlaceSerializer(serializers.ModelSerializer):
    opuser = OtherPlacesUserSerializer(many=False)
    class Meta:
        model = Place
        fields = ('id', 'opuser', 'title', 'description', 'address', 'city', 'state', 'postal_code', 'country', 'photos', 'created', 'visited', 'totalvisitors', 'saved', 'totalsaved', 'isMine')

class PlacePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacePhoto
        fields = ('id', 'photo')
        depth = 1