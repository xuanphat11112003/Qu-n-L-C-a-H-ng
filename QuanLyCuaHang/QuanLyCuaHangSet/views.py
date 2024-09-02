# myapp/views.py
from django.db import transaction
from rest_framework import status, viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import *
from .serializer import *


class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_permissions(self):
        if self.action in ['get_current_user']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method == 'PATCH':
            for k, v in request.data.items():
                setattr(user, k, v)
            user.set_password(user.password)
            user.save()

        return Response(UserSerializer(user).data)

class HoaDonViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = HoaDon.objects.filter(active=True)
    serializer_class = HoaDonSerializer

    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['post'], detail=False)
    def create_hoa_don(self, request):
        user = request.user

        try:
            # Tìm kiếm nhân viên dựa vào user hiện tại
            nhan_vien = NhanVien.objects.get(user=user)
        except NhanVien.DoesNotExist:
            return Response({"error": "User này không phải là nhân viên"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['nhan_vien'] = nhan_vien.id  # Gán nhân viên từ request.user

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():  # Đảm bảo rằng mọi thao tác dưới đây đều hoàn tất hoặc không có gì thay đổi
                hoa_don = serializer.save()

                # Xử lý logic tạo chi tiết hóa đơn
                chi_tiet_data = request.data.get('chi_tiet', [])
                for item in chi_tiet_data:
                    item['hoa_don'] = hoa_don.id
                    chi_tiet_serializer = HoaDonSPSerializer(data=item)
                    if chi_tiet_serializer.is_valid():
                        chi_tiet_serializer.save()
                    else:
                        return Response(chi_tiet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Tính toán điểm tích lũy cho khách hàng
                khach_hang = hoa_don.khach_hang
                tong_tien = hoa_don.tong_tien

                # 1000 VND = 1 điểm
                diem_tich_luy = tong_tien // 1000

                # Tạo bản ghi TichDiemVoucher cho khách hàng
                TichDiemVoucher.objects.create(
                    khach_hang=khach_hang,
                    diem=diem_tich_luy,
                    tong_tien=tong_tien,
                    ngay_lap=hoa_don.ngay_lap
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(methods=['post'], detail=False)
    def create_hoa_don_khach_hang(self, request):
        user = request.user

        try:
            # Tìm kiếm khách hàng dựa vào user hiện tại
            khach_hang = KhachHang.objects.get(user=user)
        except KhachHang.DoesNotExist:
            return Response({"error": "User này không phải là khách hàng"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['khach_hang'] = khach_hang.id  # Gán khách hàng từ request.user

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():  # Đảm bảo rằng mọi thao tác dưới đây đều hoàn tất hoặc không có gì thay đổi
                hoa_don = serializer.save()

                # Xử lý logic tạo chi tiết hóa đơn
                chi_tiet_data = request.data.get('chi_tiet', [])
                for item in chi_tiet_data:
                    item['hoa_don'] = hoa_don.id
                    chi_tiet_serializer = HoaDonSPSerializer(data=item)
                    if chi_tiet_serializer.is_valid():
                        chi_tiet_serializer.save()
                    else:
                        return Response(chi_tiet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Tính toán điểm tích lũy cho khách hàng
                tong_tien = hoa_don.tong_tien

                # 1000 VND = 1 điểm
                diem_tich_luy = tong_tien // 1000

                # Tạo bản ghi TichDiemVoucher cho khách hàng
                TichDiemVoucher.objects.create(
                    khach_hang=khach_hang,
                    diem=diem_tich_luy,
                    tong_tien=tong_tien,
                    ngay_lap=hoa_don.ngay_lap
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    @action(methods=['get'], url_path='comments', detail=True)
    def show_comments(self, request, pk=None):
        # Lấy sản phẩm dựa trên pk
        product = self.get_object()

        # Lấy các bình luận liên quan đến sản phẩm
        comments = Comment.objects.filter(product=product)

        # Serialize dữ liệu bình luận
        serializer = CommentSerializer(comments, many=True)

        # Trả về phản hồi
        return Response(serializer.data)

    @action(methods=['post'], url_path='add_comment', detail=True)
    def add_comment(self, request, pk=None):
        user = request.user
        product = self.get_object()
        content = request.data.get("content")

        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_403_FORBIDDEN)

        if not content:
            return Response({"detail": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(content=content, user=user, product=product)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

