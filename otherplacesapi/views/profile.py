"""View module for handling requests about park areas"""
import uuid
import base64
from django.core.files.base import ContentFile
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponseServerError
from rest_framework import status, serializers
from django.contrib.auth.models import User
from otherplacesapi.models import OtherPlacesUser


class OtherPlacesProfileView(ViewSet):
    """Other Places users"""

    def retrieve(self, request, pk=None):
        """Handle GET requests for single user

        Returns:
            Response -- JSON serialized other places user instance
        """
        try:
            opuser = OtherPlacesUser.objects.get(pk=pk)
            serializer = OtherPlacesUserSerializer(opuser, context={'request': request})
            return Response(serializer.data)
        except OtherPlacesUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a user

        Returns:
            Response -- Empty body with 204 status code
        """
        opuser = OtherPlacesUser.objects.get(user=request.auth.user)
        format, imgstr = request.data["profile_pic"].split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'{opuser.id}-{uuid.uuid4()}.{ext}')
        opuser.profile_pic = data
        opuser.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """Handle GET requests to user resource

        Returns:
            Response -- JSON serialized list of Other Places users
        """
        opusers = OtherPlacesUser.objects.all()

        serializer = OtherPlacesUserSerializer(
            opusers, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def myprofile(self, request):
        """Retrieve logged in user's profile"""
        try:
            opuser = OtherPlacesUser.objects.get(user=request.auth.user)
            serializer = OtherPlacesUserSerializer(opuser, context={'request': request})
            return Response(serializer.data)
        except OtherPlacesUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')


class OtherPlacesUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = OtherPlacesUser
        fields = ('id', 'user', 'bio', 'profile_pic')
