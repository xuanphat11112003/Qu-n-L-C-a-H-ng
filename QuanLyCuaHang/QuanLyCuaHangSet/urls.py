from django.urls import path,include

from django.contrib import admin
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('o/', include('oauth2_provider.urls',namespace='oauth2_provider')),
]