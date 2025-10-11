from django.db import models

# =====================
# 1. Phòng Ban
# =====================
class PhongBan(models.Model):
    TenPhongBan = models.CharField(max_length=100, unique=True)
    Email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.TenPhongBan


# =====================
# 2. Nhân Viên
# =====================
class NhanVien(models.Model):
    VaiTro_CHOICES = [
        ('VT', 'Văn thư'),
        ('QL', 'Quản lý'),
        ('NV', 'Nhân viên'),
    ]

    HoTen = models.CharField(max_length=100)
    VaiTro = models.CharField(max_length=50, choices=VaiTro_CHOICES, null=True, blank=True)
    Email = models.EmailField(unique=True)
    SDT = models.CharField(max_length=10, blank=True, null=True)
    MaPhongBan = models.ForeignKey(PhongBan, on_delete=models.CASCADE, related_name='nhanviens')

    def __str__(self):
        return self.HoTen


# =====================
# 3. Văn Bản Đến
# =====================
class VanBanDen(models.Model):
    DoKhan_CHOICES = [
        ('Thường', 'Thường'),
        ('Khẩn', 'Khẩn'),
        ('Hỏa tốc', 'Hỏa tốc'),
    ]

    DoMat_CHOICES = [

        ('Thường', 'Thường'),
        ('Mật', 'Mật'),
        ('Tối mật', 'Tối mật'),
    ]

    TrangThai_CHOICES = [
        ('Chờ xử lý', 'Chờ xử lý'),
        ('Đang xử lý', 'Đang xử lý'),
        ('Hoàn thành', 'Hoàn thành'),
    ]

    SoHieu = models.CharField(max_length=255)
    TrichYeu = models.CharField(max_length=255)
    LoaiVBDen = models.CharField(max_length=255)
    DonViPhatHanh = models.CharField(max_length=255)
    NgayBanHanh = models.DateField()
    NgayDen = models.DateField()
    NoiDung = models.TextField(blank=True, null=True)
    DoKhan = models.CharField(max_length=50, choices=DoKhan_CHOICES, default='Thường')
    DoMat = models.CharField(max_length=50, choices=DoMat_CHOICES, default='Thường')
    FileDinhKem = models.CharField(max_length=255, blank=True, null=True)
    TrangThai = models.CharField(max_length=100, choices=TrangThai_CHOICES, default='Chờ xử lý')
    MaNhanVien = models.ForeignKey(NhanVien, on_delete=models.SET_NULL, null=True, related_name='vanbanden')
    MaPhongBan = models.ForeignKey(PhongBan, on_delete=models.SET_NULL, null=True, related_name='vanbanden')

    def __str__(self):
        return f"{self.SoHieu} - {self.TrichYeu}"


# =====================
# 4. Văn Bản Đi
# =====================
class VanBanDi(models.Model):
    DoKhan_CHOICES = [
        ('Thường', 'Thường'),
        ('Khẩn', 'Khẩn'),
        ('Hỏa tốc', 'Hỏa tốc'),
    ]

    DoMat_CHOICES = [
        ('Thường', 'Thường'),
        ('Mật', 'Mật'),
        ('Tối mật', 'Tối mật'),
    ]

    SoHieu = models.CharField(max_length=50, unique=True)
    TrichYeu = models.CharField(max_length=255)
    LoaiVbDi = models.CharField(max_length=255)
    DonViNhan = models.CharField(max_length=255, blank=True, null=True)
    NgayBanHanh = models.DateField(blank=True, null=True)
    NoiDung = models.TextField()
    DinhKem = models.CharField(max_length=255, blank=True, null=True)
    DoMat = models.CharField(max_length=255, choices=DoMat_CHOICES, default='Thường')
    DoKhan = models.CharField(max_length=255, choices=DoKhan_CHOICES, default='Thường')
    TrangThai = models.CharField(max_length=255, default='Đang xử lý')
    NgayTao = models.DateTimeField(auto_now_add=True)
    MaNhanVien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='vanbandi')
    MaPhongBan = models.ForeignKey(PhongBan, on_delete=models.CASCADE, related_name='vanbandi')

    def __str__(self):
        return f"{self.SoHieu} - {self.TrichYeu}"


# =====================
# 5. Nhật Ký Hoạt Động
# =====================
class NhatKyHoatDong(models.Model):
    ThaoTac_CHOICES = [
        ('Tạo VBĐ', 'Tạo văn bản đến'),
        ('Cập nhật', 'Cập nhật văn bản'),
        ('Phê duyệt', 'Phê duyệt'),
        ('Từ chối', 'Từ chối'),
        ('Phân công', 'Phân công'),
        ('Xác nhận', 'Xác nhận'),
        ('Xử lý', 'Xử lý'),
        ('Hoàn thành', 'Hoàn thành'),
    ]

    TrangThai_CHOICES = [
        ('Chờ xét duyệt', 'Chờ xét duyệt'),
        ('Bị từ chối', 'Bị từ chối'),
        ('Chờ phân công', 'Chờ phân công'),
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Đang xử lý', 'Đang xử lý'),
        ('Hoàn thành', 'Hoàn thành'),
    ]

    ThoiGian = models.DateTimeField(auto_now_add=True)
    ThaoTac = models.CharField(max_length=255, choices=ThaoTac_CHOICES)
    TrangThai = models.CharField(max_length=255, choices=TrangThai_CHOICES)
    MaNhanVien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='nhatky')
    MaVbDen = models.ForeignKey(VanBanDen, on_delete=models.SET_NULL, null=True, blank=True, related_name='nhatky')
    MaVbDi = models.ForeignKey(VanBanDi, on_delete=models.SET_NULL, null=True, blank=True, related_name='nhatky')

    def __str__(self):
        return f"{self.ThaoTac} - {self.TrangThai}"


# =====================
# 6. Thông Báo
# =====================
class ThongBao(models.Model):
    TieuDe = models.CharField(max_length=255)
    NgayTao = models.DateTimeField(auto_now_add=True)
    MaNhanVien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='thongbaos')
    ID_VanBanDen = models.ForeignKey(VanBanDen, on_delete=models.SET_NULL, null=True, blank=True, related_name='thongbaos')
    ID_VanBanDi = models.ForeignKey(VanBanDi, on_delete=models.SET_NULL, null=True, blank=True, related_name='thongbaos')

    def __str__(self):
        return self.TieuDe


# =====================
# 7. Công Việc
# =====================
class CongViec(models.Model):
    TrangThai_CHOICES = [
        ('Chờ xác nhận', 'Chờ xác nhận'),
        ('Đang xử lý', 'Đang xử lý'),
        ('Hoàn thành', 'Hoàn thành'),
    ]

    TieuDe = models.CharField(max_length=255)
    MoTa = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    Deadline = models.DateTimeField()
    TrangThai = models.CharField(max_length=50, choices=TrangThai_CHOICES, default='Chờ xác nhận')
    MaNhanVien = models.ForeignKey(NhanVien, on_delete=models.CASCADE, related_name='congviec')
    MaVbDen = models.ForeignKey(VanBanDen, on_delete=models.SET_NULL, null=True, blank=True, related_name='congviec')
    MaVbDi = models.ForeignKey(VanBanDi, on_delete=models.SET_NULL, null=True, blank=True, related_name='congviec')

    def __str__(self):
        return self.TieuDe
