"""otherplaces URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from otherplacesapi.views import register_user, login_user
from otherplacesapi.views import OtherPlacesProfileView
from otherplacesapi.views import PlaceView
from otherplacesapi.views import PlacePhotoView


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'userprofiles', OtherPlacesProfileView, 'otherplacesuser')
router.register(r'places', PlaceView, 'place')
router.register(r'placephotos', PlacePhotoView, 'placephoto')

urlpatterns = [
    path('login', login_user),
    path('register', register_user),
    path('admin/', admin.site.urls),
    path('', include(router.urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
