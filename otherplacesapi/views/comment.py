"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from django.contrib.auth.models import User
from otherplacesapi.models import OtherPlacesUser, Comment, Place
import datetime


class CommentView(ViewSet):
    """Comments"""

    def create(self, request):
        """Handle POST operations
        """
        comment = Comment()
        comment.opuser = OtherPlacesUser.objects.get(user=request.auth.user)
        comment.place = Place.objects.get(pk=request.data["placeId"])
        comment.text = request.data["text"]
        comment.created = datetime.datetime.now()

        try:
            comment.save()
            serializer = CommentSerializer(comment, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)



    def retrieve(self, request, pk=None):
        """Handle GET requests for single comment
        """
        authuser = OtherPlacesUser.objects.get(user=request.auth.user)
        try:
            comment = Comment.objects.get(pk=pk)

            if authuser == comment.opuser:
                comment.isMine = True
            else:
                comment.isMine = False

            serializer = CommentSerializer(comment, context={'request': request})
            return Response(serializer.data)
        except Comment.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a comment
        """
        comment = Comment.objects.get(pk=pk)
        comment.text = request.data["text"]
        comment.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single comment
        """
        try:
            comment = Comment.objects.get(pk=pk)
            comment.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to comments resource
        """
        comments = Comment.objects.all()
        authuser = OtherPlacesUser.objects.get(user=request.auth.user)

        place = self.request.query_params.get('place', None)
        if place is not None:
            comments = comments.filter(place__id=place)
            
        for comment in comments:
            if authuser == comment.opuser:
                comment.isMine = True
            else:
                comment.isMine = False

        serializer = CommentSerializer(
            comments, many=True, context={'request': request})
        return Response(serializer.data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')


class OtherPlacesUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    class Meta:
        model = OtherPlacesUser
        fields = ('id', 'user', 'profile_pic')

class CommentSerializer(serializers.ModelSerializer):
    opuser = OtherPlacesUserSerializer(many=False)
    class Meta:
        model = Comment
        fields = ('id', 'opuser', 'place', 'text', 'created', 'isMine')