from rest_framework.decorators import action

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from QuanLyCuaHangSet.models import *
from QuanLyCuaHangSet.serializer import *
from rest_framework import permissions, viewsets, generics, status, parsers

from QuanLyCuaHangSet.models import HoaDon


# Create your views here.


class Response:
    pass


class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                setattr(user, k, v)
            user.set_password(user.password)
            user.save()

        return Response(UserSerializer(user).data)

class statisticViewSet(viewsets.ViewSet):
    queryset = HoaDon.objects.all()
    serializer_class = HoaDonSerializer

    def get_queryset(self, request):
        queryset = self.queryset
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        queryset = queryset.annotate(month=TruncMonth('ngay_lap')).values('month').annotate(total_revenue=Sum('tong_tien')).order_by('month')
        return queryset

