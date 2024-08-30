from django.contrib import admin
from .models import *

# Cấu hình hiển thị thông tin người dùng trong trang admin
admin.site.site_header = "Quản lý cửa hàng"
admin.site.site_title = "Trang quản lý cửa hàng"
admin.site.index_title = "Chào mừng bạn đến với trang quản lý"
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('field1', 'field2')

    # Tùy chỉnh tiêu đề của trang danh sách
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Danh sách các mục'
        return super(MyModelAdmin, self).changelist_view(request, extra_context=extra_context)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'ho_ten', 'gioi_tinh', 'nam_sinh', 'thanh_vien', 'dia_chi')
    search_fields = ('username', 'ho_ten')
    list_filter = ('gioi_tinh', 'thanh_vien')

# Cấu hình hiển thị thông tin khách hàng trong trang admin
@admin.register(KhachHang)
class KhachHangAdmin(admin.ModelAdmin):
    list_display = ('user', 'thanh_vien')
    search_fields = ('user__username',)
    list_filter = ('thanh_vien',)

# Cấu hình hiển thị thông tin nhân viên trong trang admin
@admin.register(NhanVien)
class NhanVienAdmin(admin.ModelAdmin):
    list_display = ('user', 'gio_lam')
    search_fields = ('user__username',)
    list_filter = ('gio_lam',)

# Cấu hình hiển thị thông tin nhân viên quản lý trong trang admin
@admin.register(NhanVien_QL)
class NhanVienQLAdmin(admin.ModelAdmin):
    list_display = ('user', 'phu_cap', 'nghi_phep', 'chuc_vu')
    search_fields = ('user__username', 'chuc_vu')
    list_filter = ('chuc_vu',)

# Cấu hình hiển thị thông tin voucher tích điểm trong trang admin
@admin.register(TichDiemVoucher)
class TichDiemVoucherAdmin(admin.ModelAdmin):
    list_display = ( 'ngay_lap', 'diem', 'tong_tien', 'khach_hang')
    # search_fields = ('khach_hang__user__username')
    list_filter = ('ngay_lap',)

# Cấu hình hiển thị thông tin hóa đơn trong trang admin
@admin.register(HoaDon)
class HoaDonAdmin(admin.ModelAdmin):
    list_display = ('id', 'ngay_lap', 'tong_tien', 'khach_hang', 'nhan_vien')
    search_fields = ('id', 'khach_hang__user__username', 'nhan_vien__user__username')
    list_filter = ('ngay_lap',)

# Cấu hình hiển thị thông tin sản phẩm trong trang admin
@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    list_display = ('ten_sp', 'loai', 'don_gia', 'kho_hang')
    search_fields = ('ten_sp', 'loai')
    list_filter = ('loai', 'kho_hang__ten_kho')

# Cấu hình hiển thị thông tin kho hàng trong trang admin
@admin.register(KhoHang)
class KhoHangAdmin(admin.ModelAdmin):
    list_display = ('ten_kho', 'so_luong_sp', 'trang_thai')
    search_fields = ('ten_kho',)
    list_filter = ('trang_thai',)

# Cấu hình hiển thị thông tin đánh giá của khách hàng trong trang admin
@admin.register(DanhGiaOfKhachHang)
class DanhGiaOfKhachHangAdmin(admin.ModelAdmin):
    list_display = ('khach_hang', 'nhan_vien', 'ngay_dg')
    search_fields = ('khach_hang__user__username', 'nhan_vien__user__username')
    list_filter = ('ngay_dg',)

# Cấu hình hiển thị thông tin chi tiết hóa đơn sản phẩm trong trang admin
@admin.register(HoaDon_SP)
class HoaDonSPAdmin(admin.ModelAdmin):
    list_display = ('hoa_don', 'san_pham', 'so_luong')
    search_fields = ('hoa_don__id', 'san_pham__ten_sp')
    list_filter = ('hoa_don__ngay_lap',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_date', 'user')
