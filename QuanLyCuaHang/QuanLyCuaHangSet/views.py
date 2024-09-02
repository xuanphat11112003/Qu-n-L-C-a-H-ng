# myapp/views.py
from datetime import datetime

from django.db import transaction
from rest_framework import status, viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import HoaDon, KhachHang, NhanVien, SanPham, HoaDon_SP, User, TichDiemVoucher
from .serializer import HoaDonSerializer, UserSerializer, SanPhamSerializer, HoaDonSPSerializer, NhanVienSerializer, \
    NhanVien_QLSerializer, KhachHangSerializer


class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

     @action(methods=['get', 'patch'], url_path='current-user', detail=False)
     def get_current_user(self, request):
        user = request.user

        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                if 'password' in request.data:
                    # Ensure password is hashed before saving
                    user.set_password(request.data['password'])
                    user.save(update_fields=['password'])
                serializer.save()

                # Update related models based on user role
                if user.user_role == User.UserRole.ROLE_CUSTOMER:
                    khach_hang = KhachHang.objects.get(user=user)
                    khach_hang_serializer = KhachHangSerializer(khach_hang, data=request.data, partial=True)
                    if khach_hang_serializer.is_valid():
                        khach_hang_serializer.save()
                    else:
                        return Response(khach_hang_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                elif user.user_role == User.UserRole.ROLE_USER:
                    nhan_vien = NhanVien.objects.get(user=user)
                    nhan_vien_serializer = NhanVienSerializer(nhan_vien, data=request.data, partial=True)
                    if nhan_vien_serializer.is_valid():
                        nhan_vien_serializer.save()
                    else:
                        return Response(nhan_vien_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                elif user.user_role == User.UserRole.ROLE_ADMIN:
                    nhan_vien_ql = NhanVien_QL.objects.get(user=user)
                    nhan_vien_ql_serializer = NhanVien_QLSerializer(nhan_vien_ql, data=request.data, partial=True)
                    if nhan_vien_ql_serializer.is_valid():
                        nhan_vien_ql_serializer.save()
                    else:
                        return Response(nhan_vien_ql_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(user).data)

    def get_serializer_class(self):
        # Override serializer class if needed
        return UserSerializer

class HoaDonViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = HoaDon.objects.all()
    serializer_class = HoaDonSerializer


    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return None;
        else:
            return HoaDonSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]  # Adjust permissions as needed
        else:
            return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = self.queryset

        if self.action == 'list':
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(id__icontains=q)  # Adjust filter based on your needs
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        products = data.get('products', [])  # List of products

        # Fetch KhachHang and NhanVien instances
        khach_hang = KhachHang.objects.get(id=data.get("khach_hang"))
        nhan_vien = NhanVien.objects.get(id=data.get("nhan_vien"))

        # Create HoaDon object
        hoa_don_data = {
            "ghi_chu": data.get("ghi_chu", ""),
            "tong_tien": data.get("tong_tien", 0),
            "khach_hang": khach_hang,  # Use the fetched instance
            "nhan_vien": nhan_vien,  # Use the fetched instance
        }

        hoa_don = HoaDon.objects.create(**hoa_don_data)

        # Create HoaDon_SP objects
        for product in products:
            san_pham_id = product.get('san_pham_id')
            so_luong = product.get('so_luong', 0)

            if san_pham_id:
                HoaDon_SP.objects.create(
                    hoa_don=hoa_don,
                    san_pham_id=san_pham_id,
                    so_luong=so_luong
                )

        return Response(
            HoaDonSerializer(hoa_don, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['put'], detail=True)
    def update_partial(self, request, pk=None):
        try:
            hoa_don = HoaDon.objects.get(pk=pk)
        except HoaDon.DoesNotExist:
            return Response({"error": "Hóa đơn không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HoaDonSerializer(hoa_don, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def delete(self, request, pk=None):
        try:
            hoa_don = HoaDon.objects.get(pk=pk)
            hoa_don.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except HoaDon.DoesNotExist:
            return Response({"error": "Hóa đơn không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

class StatisticViewSet(viewsets.ViewSet):
    queryset = HoaDon.objects.all()
    serializer_class = HoaDonSerializer

    def get_queryset(self):
        queryset = self.queryset
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(ngay_lap__year=year, ngay_lap__month=month)
        queryset = queryset.annotate(month=TruncMonth('ngay_lap')).values('month').annotate(total_revenue=Sum('tong_tien')).order_by('month')
        return queryset

class SanPhamViewSet(viewsets.ModelViewSet):
    queryset = SanPham.objects.filter(active=True)
    serializer_class = SanPhamSerializer
