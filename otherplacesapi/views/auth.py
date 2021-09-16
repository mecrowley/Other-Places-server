import uuid
import base64
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from otherplacesapi.models import OtherPlacesUser


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data['username']
    password = request.data['password']

    authenticated_user = authenticate(username=username, password=password)
    if authenticated_user is not None:
        # use ORM to get the token for this user
        token = Token.objects.get(user=authenticated_user)
        data = {
            'valid': True,
            'token': token.key,
            'isAdmin': authenticated_user.is_staff
        }
        return Response(data)
    else:
        data = {'valid': False}
        return Response(data)

@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    new_user = User.objects.create_user(
        username=request.data['username'],
        email=request.data['email'],
        password=request.data['password'],
        first_name=request.data['first_name'],
        last_name=request.data['last_name']
    )

    if request.data["profile_pic"] != {}:
        format, imgstr = request.data["profile_pic"].split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
    else:
        data = None

    otherplacesuser = OtherPlacesUser.objects.create(
        user=new_user,
        bio=request.data['bio'],
        profile_pic=data
    )

    token = Token.objects.create(user=otherplacesuser.user)

    data = {'token': token.key}

    return Response(data)
