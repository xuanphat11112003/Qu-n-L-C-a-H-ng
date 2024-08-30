from rest_framework.decorators import action

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from QuanLyCuaHangSet.models import *
from QuanLyCuaHangSet.serializer import *
from rest_framework import permissions, viewsets, generics, status, parsers

from QuanLyCuaHangSet.models import HoaDon
from . import serializer
from rest_framework.response import Response

# Create your views here.



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

class HoaDonViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = HoaDon.objects.filter(active=True)
    serializer_class = HoaDonSerializer

    @action(methods=['post'], url_path='add', detail=False)
    def them(self, request):
        data = request.data
        tong_tien = data.get('tong_tien')
        ghi_chu = data.get('ghi_chu')
        khach_hang = KhachHang.objects.get(id = data.get('khach_hang'))
        nhan_vien = NhanVien.objects.get(id = data.get('nhan_vien'))

        hoaDon = HoaDon.objects.create(tong_tien=tong_tien, ghi_chu=ghi_chu, khach_hang=khach_hang, nhan_vien=nhan_vien)
        return Response(serializer.HoaDonSerializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['put'], url_path='update', detail=True)
    def sua(self, request, pk):
        try:
            hoaDon = HoaDon.objects.get(pk=pk)
        except HoaDon.DoesNotExist:
            return Response({"error": "Hoa don khong ton tai"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HoaDonSerializer(HoaDon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)