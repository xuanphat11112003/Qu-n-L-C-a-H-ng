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

    def create(self, validated_data):
        # Tách password ra khỏi validated_data để xử lý đặc biệt
        password = validated_data.pop('password')

        # Tạo instance User từ validated_data
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Kiểm tra vai trò của user để tạo KhachHang, NhanVien hoặc NhanVien_QL tương ứng
        if user.user_role == User.UserRole.ROLE_CUSTOMER:
            # Tạo KhachHang nếu vai trò là ROLE_CUSTOMER
            KhachHang.objects.get_or_create(user=user)
        elif user.user_role == User.UserRole.ROLE_USER:
            # Tạo NhanVien nếu vai trò là ROLE_USER
            NhanVien.objects.get_or_create(user=user, defaults={'gio_lam': 0})  # Thiết lập giá trị mặc định cho 'gio_lam'
        elif user.user_role == User.UserRole.ROLE_ADMIN:
            # Tạo NhanVien_QL nếu vai trò là ROLE_ADMIN
            NhanVien_QL.objects.get_or_create(
                user=user,
                defaults={
                    'phu_cap': 0,
                    'nghi_phep': 0,
                    'chuc_vu': 'Quản lý'
                }
            )

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
class KhachHangSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = KhachHang
        fields = ['id', 'user', 'thanh_vien']
        read_only_fields = ['id']

class NhanVienSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = NhanVien
        fields = ['id', 'user', 'gio_lam']
        read_only_fields = ['id']

class NhanVien_QLSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = NhanVien_QL
        fields = ['id', 'user', 'phu_cap', 'nghi_phep', 'chuc_vu']
        read_only_fields = ['id']
