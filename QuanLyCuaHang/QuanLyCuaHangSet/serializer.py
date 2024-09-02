# myapp/serializers.py
from django.db.models import Sum
from rest_framework import serializers
from .models import HoaDon, HoaDon_SP, KhachHang, NhanVien, User, SanPham, TichDiemVoucher


class UserSerializer(serializers.ModelSerializer):
    diem_tich_luy = serializers.SerializerMethodField()

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()

        if data.get('user_role') == "ROLE_CUSTOMER":
            KhachHang.objects.get_or_create(user=user)


        elif user.user_role == User.UserRole.ROLE_USER:

            NhanVien.objects.get_or_create(user=user, defaults={'gio_lam': 0})
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



class HoaDonSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoaDon
        fields = '__all__'

class HoaDonSPSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoaDon_SP
        fields = '__all__'

class SanPhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SanPham
        fields = '__all__'
