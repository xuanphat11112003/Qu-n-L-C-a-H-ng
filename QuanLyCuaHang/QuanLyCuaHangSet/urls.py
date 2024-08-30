from django.urls import path,include
from QuanLyCuaHangSet import views
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from QuanLyCuaHangSet.views import SanPhamViewSet

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('statistic', views.StatisticViewSet, basename='statistic')
router.register('hoadon', views.HoaDonViewSet, basename='hoadon')
router.register('sanpham', SanPhamViewSet, basename ='sanpham')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('o/', include('oauth2_provider.urls',namespace='oauth2_provider')),
]