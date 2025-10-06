from django.db import models

class PhongBan(models.Model):
    ten_phong_ban = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ten_phong_ban


class NhanVien(models.Model):
    VAITRO_CHOICES = [
        ('NV', 'Nhân Viên'),
        ('QL', 'Quản Lý'),
        ('VT', 'Văn Thư'),
    ]

    ho_ten = models.CharField(max_length=100)
    vai_tro = models.CharField(max_length=100, choices=VAITRO_CHOICES, null=True, blank=True)
    email = models.EmailField(unique=True)
    sdt = models.CharField(max_length=10)
    phong_ban = models.ForeignKey(PhongBan, on_delete=models.CASCADE, related_name='nhan_viens')

    def __str__(self):
        return self.ho_ten
from django.db import models

# Create your models here.
from django.db import models

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
    DoKhan = models.CharField( default="BINH THUONG", choices=DOKHAN_CHOICES, max_length=50)
    DoMat = models.CharField( choices=DOMAT_CHOICES, default="BINH THUONG", max_length=50)
    FileDinhKem = models.FileField(upload_to='vanbanden/', blank=True)
    MaNhanVien = models.ForeignKey(NhanVien, on_delete =models.CASCADE)
    MaPhongBan = models.ForeignKey(PhongBan, on_delete = models.CASCADE)
    def __str__(self):
        return self.TrichYeu

class ThongBao(models.Model):
    TieuDe = models.TextField(null = False)
    NgayTao = models.DateTimeField(auto_now_add=True)
    MaNhanVien = models.ForeignKey(NhanVien, on_delete = models.CASCADE)
    MaVBDen = models.ForeignKey(VanBanDen, on_delete = models.CASCADE)
    MaVBDi = models.ForeignKey(VanBanDi, on_delete = models.CASCADE)
    def __str__(self):
        return self.TieuDe

class NhatKiCongVien(models.Model):
    class TrangThai(models.TextChoices):
        Choxetduyet = "Cho xet duyet", "CHO XET DUYET"
        BiTuChoi = "Bi tu choi", "BI TU CHOI"
        ChoPhanCong = "Cho phan cong", "CHO PHAN CONG"
        ChoXacNhan = "Cho xac nhan", "CHO XAC NHAN"
        DangXuLY = "Dang xu li", "DANG XU LI"
        HoanThanh = "Hoan thanh", "HOAN THANH"
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





