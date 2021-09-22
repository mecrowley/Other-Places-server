"""View module for handling requests about park areas"""
import uuid
import base64
from django.core.files.base import ContentFile
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponseServerError
from rest_framework import status, serializers
from django.db.models import Q
from django.contrib.auth.models import User
from otherplacesapi.models import OtherPlacesUser, Follow


class OtherPlacesProfileView(ViewSet):
    """Other Places users"""

    def retrieve(self, request, pk=None):
        """Handle GET requests for single user

        Returns:
            Response -- JSON serialized other places user instance
        """
        try:
            authuser = OtherPlacesUser.objects.get(user=request.auth.user)
            opuser = OtherPlacesUser.objects.get(pk=pk)
            following = Follow.objects.filter(Q(opuser=opuser) & Q(follower=authuser))
            
            if following:
                opuser.following = True
            else:
                opuser.following = False

            if authuser == opuser:
                opuser.isMe = True
            else:
                opuser.isMe = False
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
        opuser.bio = request.data["bio"]
        splitprofilepic = request.data["profile_pic"].split("/")
        if splitprofilepic[0] == "http:":
            pass
        else:
            format, imgstr = request.data["profile_pic"].split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
            opuser.profile_pic = data
        opuser.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """Handle GET requests to user resource

        Returns:
            Response -- JSON serialized list of Other Places users
        """
        opusers = OtherPlacesUser.objects.all()
        authuser = OtherPlacesUser.objects.get(user=request.auth.user)
        for opuser in opusers:
            if opuser == authuser:
                opuser.isMe = True
            else:
                opuser.isMe = False

        serializer = OtherPlacesUserSerializer(
            opusers, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def myprofile(self, request):
        """Retrieve logged in user's profile"""
        try:
            opuser = OtherPlacesUser.objects.get(user=request.auth.user)
            opuser.isMe = True
            serializer = OtherPlacesUserSerializer(opuser, context={'request': request})
            return Response(serializer.data)
        except OtherPlacesUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=['post', 'delete'], detail=True)
    def follow(self, request, pk=None):
        """Managing users saving a place"""
        authuser = OtherPlacesUser.objects.get(user=request.auth.user)
        opuser = None
        try:
            opuser = OtherPlacesUser.objects.get(pk=pk)
        except OtherPlacesUser.DoesNotExist:
            return Response(
                {'message': 'Place does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == "POST":
            try:
                follow = Follow()
                follow.follower = authuser
                follow.opuser = opuser
                follow.save()
                return Response({}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({'message': ex.args[0]})

        elif request.method == "DELETE":
            try:
                follow = Follow.objects.filter(Q(opuser=opuser) & Q(follower=authuser))
                follow.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]})

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'date_joined')


class OtherPlacesUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = OtherPlacesUser
        fields = ('id', 'user', 'bio', 'profile_pic', 'isMe', 'following')
