from django.urls import path,include
from QuanLyCuaHangSet import views
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from QuanLyCuaHangSet.views import *

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('statistic', views.StatisticViewSet, basename='statistic')
router.register('hoadon', views.HoaDonViewSet, basename='hoadon')
router.register('sanpham', SanPhamViewSet, basename ='sanpham')
router.register('comments', views.CommentViewSet, basename='comments')
router.register('diachigiaohang', views.CommentViewSet, basename='diachigiaohang')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('o/', include('oauth2_provider.urls',namespace='oauth2_provider')),
    path('pay', views.index, name='index'),
    path('payment', views.payment, name='payment'),
    path('payment_ipn', views.payment_ipn, name='payment_ipn'),
    path('payment_return', views.payment_return, name='payment_return'),
    path('query',views.query, name='query'),
    path('refund',views.refund, name='refund'),
]