from django.db import models

# =====================
# 1. Phòng Ban
# =====================
class PhongBan(models.Model):
    TenPhongBan = models.CharField(max_length=100, unique=True)
    Email = models.EmailField(unique=True)

    def __str__(self):
        return self.TenPhongBan

class NhanVien(models.Model):
    VAITRO_CHOICES = [
        ('NV', 'Nhân Viên'),
        ('QL', 'Quản Lý'),
        ('VT', 'Văn Thư'),
        ('TP', 'Trưởng Phòng')
    ]

    HoTen = models.CharField(max_length=100)
    VaiTro = models.CharField(max_length=100, choices=VAITRO_CHOICES, null=True, blank=True)
    Email = models.EmailField(unique=True)
    SDT = models.CharField(max_length=10)
    PhongBan = models.ForeignKey(PhongBan, on_delete=models.CASCADE, related_name='nhan_viens')

    def __str__(self):
        return self.HoTen

DOKHAN_CHOICES  = [
    ('KHAN', 'Khẩn'),
    ('BINH THUONG', 'Bình thường'),
]

DOMAT_CHOICES  = [
    ('MAT', "Mật"),
    ('BINH THUONG', 'Bình thường')
]

class VanBanDen(models.Model):
    SoHieu = models.CharField(null = False, max_length = 100)
    TrichYeu = models.CharField(null = False, max_length = 250)
    LoaiVBDen = models.CharField(max_length = 100)
    DonViPhatHanh = models.CharField(max_length = 250)
    NgayBanHanh = models.DateTimeField(null = False)
    NgayDen = models.DateTimeField(null = False)
    NoiDung = models.CharField(max_length = 250)
    TrangThai = models.CharField(max_length=50, default="Chờ xét duyệt")
    DoKhan = models.CharField( default="BINH THUONG", choices=DOKHAN_CHOICES, max_length=50)
    DoMat = models.CharField( choices=DOMAT_CHOICES, default="BINH THUONG", max_length=50)
    FileDinhKem = models.FileField(upload_to='vanbanden/', blank=True)
    MaNhanVien = models.ForeignKey(NhanVien, on_delete =models.CASCADE)
    MaPhongBan = models.ForeignKey(PhongBan, on_delete = models.CASCADE)
    def __str__(self):
        return self.TrichYeu

class VanBanDi(models.Model):
    # id = models.AutoField(primary_key=True)  # ID
    SoHieu = models.CharField(max_length=50, unique=True)  # SoHieu
    NgayBanHanh = models.DateField(null=True, blank=True)  # NgayBanHanh
    TrichYeu = models.CharField(max_length=500)  # TrichYeu
    NoiDung = models.TextField()  # NoiDung
    LoaiVbDi = models.CharField(max_length=255)  # LoaiVbDi
    DonViNhan = models.CharField(max_length=255, null=True, blank=True)  # DonViNhan
    Email = models.EmailField(blank=False)
    FileDinhKem = models.FileField(upload_to='vanbandi/', blank=True)
    DoMat = models.CharField(max_length=255, null=True, blank=True)  # DoMat
    DoKhan = models.CharField(max_length=255, null=True, blank=True)  # DoKhan
    TrangThai = models.CharField(max_length=255, null=True, blank=True)  # TrangThai
    NgayTao = models.DateTimeField(auto_now_add=True)  # NgayTao
    MaNhanVien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)  # MaNhanVien

    def __str__(self):
        return self.TrichYeu

class ThongBao(models.Model):
   TieuDe = models.TextField(null=False)
   NoiDung = models.TextField(null=True, blank=True)
   NgayTao = models.DateTimeField(auto_now_add=True)
   DaDoc = models.BooleanField(default=False)
   MaNhanVien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
   MaVBDen = models.ForeignKey(VanBanDen, on_delete=models.CASCADE, null=True, blank=True)
   MaVBDi = models.ForeignKey(VanBanDi, on_delete=models.CASCADE, null=True, blank=True)

   def __str__(self):
       return self.TieuDe

class NhatKyCongViec(models.Model):
    class TrangThai(models.TextChoices):
        Choxetduyet = "Chờ xét duyêt", "CHỜ XÉT DUYỆT"
        BiTuChoi = "Bị từ chối", "BỊ TỪ CHỐI"
        ChoPhanCong = "Chờ phân công", "CHỜ PHÂN CÔNG"
        ChoXacNhan = "Chờ xác nhận", "CHỜ XÁC NHẬN"
        DangXuLy = "Đang xử lý", "ĐANG XỬ LÝ"
        HoanThanh = "Hoàn thành", "HOÀN THÀNH"
        ChoBanHanh = "Chờ ban hành", "CHỜ BAN HÀNH"
        BanHanh = "Đã ban hành", "ĐÃ BAN HÀNH"
    TieuDe = models.CharField(null = False, max_length = 100)
    MoTa = models.TextField(max_length = 250)
    ThaoTac = models.TextField()
    TrangThai = models.CharField(choices=TrangThai.choices, null = False, max_length = 50 )
    NgayTao = models.DateTimeField(auto_now_add=True)
    HanChot = models.DateTimeField(null = False)
    MaNhanVien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
    MaVBDen = models.ForeignKey(VanBanDen, on_delete=models.CASCADE)
    MaVBDi = models.ForeignKey(VanBanDi, on_delete=models.CASCADE)
    def __str__(self):
        return self.TieuDe

