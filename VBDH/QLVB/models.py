from django.db import models
from django.conf import settings




# =====================
# 1. Phòng Ban
# =====================
class PhongBan(models.Model):
    TenPhongBan = models.CharField(max_length=100, unique=True)
    Email = models.EmailField(unique=True)

    def __str__(self):
        return self.TenPhongBan


# =====================
# 2. Văn bản đến
# =====================
DOKHAN_CHOICES = [
   ('KHAN', 'Khẩn'),
   ('BINH THUONG', 'Bình thường'),
   ('HOA TOC', 'Hỏa tốc'),  # Thêm Hỏa tốc
]

DOMAT_CHOICES = [
   ('MAT', 'Mật'),
   ('TOI MAT', 'Tối mật'),  # Thêm Tối mật
   ('BINH THUONG', 'Bình thường'),
]


class VanBanDen(models.Model):
   SoHieu = models.CharField(max_length=100, blank=False)
   TrichYeu = models.CharField(max_length=250, blank=False)
   LoaiVBDen = models.CharField(max_length=100)
   DonViPhatHanh = models.CharField(max_length=250)
   NgayBanHanh = models.DateTimeField(null=True, blank=True)
   NgayDen = models.DateTimeField(null=True, blank=True)
   NoiDung = models.CharField(max_length=500, null=True, blank=True)
   DoKhan = models.CharField(
       max_length=20,
       choices=DOKHAN_CHOICES,
       default='BINH THUONG'
   )
   DoMat = models.CharField(
       max_length=20,
       choices=DOMAT_CHOICES,
       default='BINH THUONG'
   )
   TrangThai = models.CharField(max_length=50, null=True, blank=True)
   FileDinhKem = models.FileField(upload_to='vanbanden/', blank=True, null=True)
   MaNhanVien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   MaPhongBan = models.ForeignKey(PhongBan, on_delete=models.CASCADE)


   def __str__(self):
       return self.TrichYeu




# =====================
# 3. Văn bản đi – ĐÃ SỬA HOÀN CHỈNH
# =====================
DO_KHAN_VBDI_CHOICES = [
   ('BINH THUONG', 'Bình thường'),
   ('KHAN', 'Khẩn'),
   ('HOA TOC', 'Hỏa tốc'),
]


DO_MAT_VBDI_CHOICES = [
   ('BINH THUONG', 'Bình thường'),
   ('MAT', 'Mật'),
   ('TOI MAT', 'Tối mật'),
]




class VanBanDi(models.Model):
   SoHieu = models.CharField(max_length=50, unique=True)
   NgayBanHanh = models.DateField(null=True, blank=True)
   TrichYeu = models.CharField(max_length=500)
   NoiDung = models.TextField()
   LoaiVbDi = models.CharField(max_length=255)
   DonViNhan = models.CharField(max_length=255, null=True, blank=True)
   Email = models.EmailField(blank=False)  # Bắt buộc
   FileDinhKem = models.FileField(upload_to='vanbandi/', blank=True, null=True)


   # SỬA: thêm choices + max_length hợp lý
   DoMat = models.CharField(
       max_length=20,
       choices=DO_MAT_VBDI_CHOICES,
       default='BINH THUONG',
       null=True, blank=True
   )
   DoKhan = models.CharField(
       max_length=20,
       choices=DO_KHAN_VBDI_CHOICES,
       default='BINH THUONG',
       null=True, blank=True
   )


   TrangThai = models.CharField(max_length=50, null=True, blank=True)
   NgayTao = models.DateTimeField(auto_now_add=True)
   MaNhanVien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   MaVBDen = models.ForeignKey(VanBanDen, on_delete=models.CASCADE, null=True, blank=True)


   def __str__(self):
       return self.TrichYeu


   # TỰ ĐỘNG TẠO get_..._display
   def get_DoMat_display(self):
       return dict(DO_MAT_VBDI_CHOICES).get(self.DoMat, self.DoMat)


   def get_DoKhan_display(self):
       return dict(DO_KHAN_VBDI_CHOICES).get(self.DoKhan, self.DoKhan)




# =====================
# 4. Thông báo
# =====================
class ThongBao(models.Model):
   TieuDe = models.CharField(max_length=255)  # Dùng CharField thay TextField
   NoiDung = models.TextField(null=True, blank=True)
   NgayTao = models.DateTimeField(auto_now_add=True)
   DaDoc = models.BooleanField(default=False)
   MaNhanVien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   MaVBDen = models.ForeignKey(VanBanDen, on_delete=models.CASCADE, null=True, blank=True)
   MaVBDi = models.ForeignKey(VanBanDi, on_delete=models.CASCADE, null=True, blank=True)


   def __str__(self):
       return self.TieuDe


    def __str__(self):
        return self.TieuDe


# =====================
# 5. Phân công công việc
# =====================
class PhanCongCongViec(models.Model):
   TieuDe = models.CharField(max_length=100)
   MoTa = models.TextField(max_length=500)
   NgayTao = models.DateTimeField(auto_now_add=True)
   HanChot = models.DateTimeField()
   NguoiGiao = models.ForeignKey(
       settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ds_cong_viec_giao'
   )
   NguoiNhan = models.ForeignKey(
       settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ds_cong_viec_duoc_giao'
   )
   VanBanDen = models.ForeignKey('VanBanDen', on_delete=models.CASCADE, null=True, blank=True)
   VanBanDi = models.ForeignKey('VanBanDi', on_delete=models.CASCADE, null=True, blank=True)


   class TrangThai(models.TextChoices):
       CHO_XET_DUYET = "Chờ xét duyệt", "CHỜ XÉT DUYỆT"
       BI_TU_CHOI = "Bị từ chối", "BỊ TỪ CHỐI"
       CHO_PHAN_CONG = "Chờ phân công", "CHỜ PHÂN CÔNG"
       CHO_XAC_NHAN = "Chờ xác nhận", "CHỜ XÁC NHẬN"
       DANG_XU_LY = "Đang xử lý", "ĐANG XỬ LÝ"
       HOAN_THANH = "Hoàn thành", "HOÀN THÀNH"
       CHO_BAN_HANH = "Chờ ban hành", "CHỜ BAN HÀN"
       DA_BAN_HANH = "Đã ban hành", "ĐÃ BAN HÀNH"


   TrangThai = models.CharField(max_length=50, choices=TrangThai.choices, default=TrangThai.CHO_XET_DUYET)


   def __str__(self):
       return f"{self.TieuDe} ({self.NguoiNhan})"




# =====================
# 6. Nhật ký công việc
# =====================
class NhatKyCongViec(models.Model):
   class TrangThai(models.TextChoices):
       CHO_XET_DUYET = "Chờ xét duyệt", "CHỜ XÉT DUYỆT"
       BI_TU_CHOI = "Bị từ chối", "BỊ TỪ CHỐI"
       CHO_PHAN_CONG = "Chờ phân công", "CHỜ PHÂN CÔNG"
       CHO_XAC_NHAN = "Chờ xác nhận", "CHỜ XÁC NHẬN"
       DANG_XU_LY = "Đang xử lý", "ĐANG XỬ LÝ"
       HOAN_THANH = "Hoàn thành", "HOÀN THÀNH"
       CHO_BAN_HANH = "Chờ ban hành", "CHỜ BAN HÀN"
       DA_BAN_HANH = "Đã ban hành", "ĐÃ BAN HÀNH"


   PhanCong = models.ForeignKey(
       PhanCongCongViec, on_delete=models.CASCADE, related_name='nhatky', null=True, blank=True
   )
   ThoiGian = models.DateTimeField(auto_now_add=True)
   ThaoTac = models.TextField()
   TrangThai = models.CharField(max_length=50, choices=TrangThai.choices)
   NguoiThucHien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


   def __str__(self):
       return f"{self.PhanCong.TieuDe if self.PhanCong else 'N/A'} - {self.get_TrangThai_display()}"


