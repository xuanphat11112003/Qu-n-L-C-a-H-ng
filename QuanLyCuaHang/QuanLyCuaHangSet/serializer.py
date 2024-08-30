# myapp/serializers.py
from django.db.models import Sum
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    diem_tich_luy = serializers.SerializerMethodField()

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()
        # Tạo KhachHang nếu chưa tồn tại và người dùng là khách hàng
        if data.get('thanh_vien', False):
            KhachHang.objects.get_or_create(user=user)
        return user

    def get_diem_tich_luy(self, obj):
        if obj.thanh_vien:  # Kiểm tra xem người dùng có phải là khách hàng không
            try:
                # Lấy thông tin khách hàng từ user
                khach_hang = KhachHang.objects.get(user=obj)
                # Tính tổng điểm từ các voucher tích lũy của khách hàng
                tong_diem = TichDiemVoucher.objects.filter(khach_hang=khach_hang).aggregate(total_diem=Sum('diem'))['total_diem']
                return tong_diem or 0  # Trả về 0 nếu không có điểm
            except KhachHang.DoesNotExist:
                return 0
        return None  # Không hiển thị điểm tích lũy nếu không phải khách hàng

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'user_role', 'diem_tich_luy']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class HoaDonSPSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoaDon_SP
        fields = ['id', 'hoa_don', 'san_pham', 'so_luong']

class HoaDonSerializer(serializers.ModelSerializer):
    chi_tiet = HoaDonSPSerializer(many=True)

    class Meta:
        model = HoaDon
        fields = ['id', 'ngay_lap', 'tong_tien', 'ghi_chu', 'khach_hang', 'nhan_vien', 'chi_tiet']


    def create(self, validated_data):
            chi_tiet_data = validated_data.pop('chi_tiet')
            hoa_don = HoaDon.objects.create(**validated_data)

            # Tạo chi tiết hóa đơn
            for item in chi_tiet_data:
                HoaDon_SP.objects.create(hoa_don=hoa_don, **item)

            # Tính toán điểm tích lũy cho khách hàng
            khach_hang = validated_data['khach_hang']
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

            return hoa_don

class SanPhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SanPham
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'user']