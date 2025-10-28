from django.contrib import admin
from .models import (
    PhongBan, NhanVien, VanBanDen, VanBanDi,
    ThongBao, PhanCongCongViec, NhatKyCongViec
)

@admin.register(PhongBan)
class PhongBanAdmin(admin.ModelAdmin):
    list_display = ('TenPhongBan', 'Email')
    search_fields = ('TenPhongBan', 'Email')

@admin.register(NhanVien)
class NhanVienAdmin(admin.ModelAdmin):
    list_display = ('HoTen', 'Email', 'SDT', 'VaiTro', 'MaPhongBan')
    list_filter = ('VaiTro', 'MaPhongBan')
    search_fields = ('HoTen', 'Email')

@admin.register(VanBanDen)
class VanBanDenAdmin(admin.ModelAdmin):
    list_display = ('SoHieu', 'TrichYeu', 'DonViPhatHanh', 'DoKhan', 'DoMat', 'TrangThai', 'MaNhanVien')
    list_filter = ('DoKhan', 'DoMat', 'TrangThai')
    search_fields = ('SoHieu', 'TrichYeu')

@admin.register(VanBanDi)
class VanBanDiAdmin(admin.ModelAdmin):
    list_display = ('SoHieu', 'TrichYeu', 'NgayBanHanh', 'Email', 'DoMat', 'DoKhan')
    list_filter = ('DoKhan', 'DoMat', 'TrangThai')
    search_fields = ('SoHieu', 'TrichYeu')

@admin.register(ThongBao)
class ThongBaoAdmin(admin.ModelAdmin):
    list_display = ('TieuDe', 'NgayTao', 'DaDoc', 'MaNhanVien')
    list_filter = ('DaDoc',)
    search_fields = ('TieuDe',)

@admin.register(PhanCongCongViec)
class PhanCongCongViecAdmin(admin.ModelAdmin):
    list_display = ('TieuDe', 'NguoiGiao', 'NguoiNhan', 'TrangThai', 'HanChot')
    list_filter = ('TrangThai',)
    search_fields = ('TieuDe',)

@admin.register(NhatKyCongViec)
class NhatKyCongViecAdmin(admin.ModelAdmin):
    list_display = ('PhanCong', 'NguoiThucHien', 'TrangThai', 'ThoiGian')
    list_filter = ('TrangThai',)
    search_fields = ('PhanCong__TieuDe',)
