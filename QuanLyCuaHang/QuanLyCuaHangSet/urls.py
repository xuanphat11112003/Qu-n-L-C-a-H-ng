from django.urls import path,include
from . import views


from django.contrib import admin
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('survey', views.statisticViewSet, basename='statistic')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('o/', include('oauth2_provider.urls',namespace='oauth2_provider')),
]