from django.db import models
from django.conf import settings
from .constants import (
   TrangThaiCongViec,
   DOKHAN_CHOICES,
   DOMAT_CHOICES,
   DO_KHAN_VBDI_CHOICES,
   DO_MAT_VBDI_CHOICES,
)




# =====================
# 1. Phòng Ban
# =====================
class PhongBan(models.Model):
    TenPhongBan = models.CharField(max_length=100, unique=True)
    Email = models.EmailField(unique=True)

    def __str__(self):
        return self.TenPhongBan

    class Meta:
        verbose_name = "Phòng ban"
        verbose_name_plural = "Phòng ban"


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

class TraCuu(models.Model):
   class Meta:
       managed = False
       permissions = [("tracuu_hethong", "Tra cứu toàn hệ thống")]
       verbose_name = "Tra cứu"
       verbose_name_plural = "Tra cứu"

class VanBanDen(models.Model):
    SoHieu = models.CharField("Số hiệu", max_length=100)
    TrichYeu = models.CharField("Trích yếu", max_length=250)
    LoaiVBDen = models.CharField("Loại văn bản", max_length=100)
    DonViPhatHanh = models.CharField("Đơn vị phát hành", max_length=250)
    NgayBanHanh = models.DateTimeField("Ngày ban hành", null=True, blank=True)

    NgayDen = models.DateTimeField("Ngày đến", null=True, blank=True)
    NoiDung = models.CharField("Nội dung tóm tắt", max_length=500, null=True, blank=True)
    DoKhan = models.CharField(max_length=20, choices=DOKHAN_CHOICES, default='BINH THUONG')
    DoMat = models.CharField(max_length=20, choices=DOMAT_CHOICES, default='BINH THUONG')
    TrangThai = models.CharField("Trạng thái", max_length=50, null=True, blank=True)
    FileDinhKem = models.FileField(upload_to='vanbanden/', blank=True, null=True)

    MaNhanVien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name="Người tiếp nhận")
    MaPhongBan = models.ForeignKey(PhongBan, on_delete=models.CASCADE,verbose_name="Phòng ban")
    NgayTao = models.DateTimeField(auto_now_add=True)
    YeuCauVBDi = models.IntegerField(choices=[(0, 'Không yêu cầu'), (1, 'Có yêu cầu')], default=0)
    NguoiNhanTrinhKy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='vanbanden_trinhky',
        verbose_name='Người Nhận Trình Ký'
    )

    def __str__(self):
        return self.TrichYeu

    class Meta:
        verbose_name = "Văn bản đến"
        verbose_name_plural = "Văn bản đến"
        permissions = [
            ("tao_vanbanden", "Tạo văn bản đến"),
            ("sua_vanbanden", "Sửa văn bản đến"),
            ("xemchitiet_vanbanden", "Xem chi tiết văn bản đến"),
            ("xemdanhsach_vanbanden", "Xem danh sách văn bản đến"),
            ("phancong_vanbanden", "Phân công nhân viên (văn bản đến)"),
            ("xetduyet_vanbanden", "Xét duyệt văn bản đến"),
            ("capnhat_trangthai_cv_vbden", "Cập nhật trạng thái công việc"),
            ("xem_nhatky_vanbanden", "Xem nhật ký hoạt động văn bản đến"),
        ]


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
    SoHieu = models.CharField("Số hiệu", max_length=50, unique=True)
    NgayBanHanh = models.DateField("Ngày ban hành", null=True, blank=True)
    TrichYeu = models.CharField("Trích yếu", max_length=500)
    NoiDung = models.TextField("Nội dung")
    LoaiVbDi = models.CharField("Loại văn bản đi", max_length=255)
    DonViNhan = models.CharField("Đơn vị nhận", max_length=255, null=True, blank=True)
    Email = models.EmailField("Email nhận")
    FileDinhKem = models.FileField(upload_to='vanbandi/', blank=True, null=True)
    DoMat = models.CharField(max_length=20, choices=DO_MAT_VBDI_CHOICES, default='BINH THUONG', null=True, blank=True)
    DoKhan = models.CharField(max_length=20, choices=DO_KHAN_VBDI_CHOICES, default='BINH THUONG', null=True, blank=True)
    TrangThai = models.CharField("Trạng thái", max_length=50, null=True, blank=True)
    NgayTao = models.DateTimeField("Ngày tạo", auto_now_add=True)

    MaNhanVien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người soạn thảo")
    MaVBDen = models.ForeignKey(VanBanDen, on_delete=models.CASCADE, null=True, blank=True,
                                verbose_name="Văn bản đến liên quan")


    YeuCauVBDi = models.IntegerField(choices=[(0, 'Không yêu cầu'), (1, 'Có yêu cầu')], default=0)
    MaPhongBan = models.ForeignKey(PhongBan, on_delete=models.CASCADE)

    def __str__(self):
       return self.TrichYeu

    class Meta:
       verbose_name = "Văn bản đi / dự thảo"
       verbose_name_plural = "Văn bản đi / dự thảo"
       permissions = [
           ("tao_vanbandi", "Tạo văn bản đi"),
           ("sua_vanbandi", "Sửa văn bản đi"),
           ("xemchitiet_vanbandi", "Xem chi tiết văn bản đi"),
           ("xemdanhsach_vanbandi", "Xem danh sách văn bản đi"),
           ("thongqua_vanbandi", "Thông qua văn bản đi"),
           ("xetduyet_vanbandi", "Xét duyệt văn bản đi"),
           ("phancong_vanbandi", "Phân công nhân viên (văn bản đi)"),
           ("banhanh_vanbandi", "Ban hành văn bản đi"),
       ]

   # TỰ ĐỘNG TẠO get_..._display
    def get_DoMat_display(self):
       return dict(DO_MAT_VBDI_CHOICES).get(self.DoMat, self.DoMat)


    def get_DoKhan_display(self):
       return dict(DO_KHAN_VBDI_CHOICES).get(self.DoKhan, self.DoKhan)




# =====================
# 4. Thông báo
# =====================
class ThongBao(models.Model):
    TieuDe = models.CharField("Tiêu đề", max_length=255)
    NoiDung = models.TextField("Nội dung", null=True, blank=True)
    NgayTao = models.DateTimeField("Ngày tạo", auto_now_add=True)
    DaDoc = models.BooleanField("Đã đọc", default=False)
    MaNhanVien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người nhận")
    MaVBDen = models.ForeignKey(VanBanDen, on_delete=models.CASCADE, null=True, blank=True)
    MaVBDi = models.ForeignKey(VanBanDi, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.TieuDe

    class Meta:
        permissions = [("xem_thongbao", "Xem thông báo")]


# =====================
# 5. Phân công công việc
# =====================
class PhanCongCongViec(models.Model):
   TieuDe = models.CharField("Tiêu đề", max_length=100)
   MoTa = models.TextField("Mô tả", max_length=500)
   NgayTao = models.DateTimeField(auto_now_add=True)
   HanChot = models.DateTimeField("Hạn chót")


   NguoiGiao = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cv_giao', verbose_name="Người giao")
   NguoiNhan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cv_nhan', verbose_name="Người nhận")
   VanBanDen = models.ForeignKey(VanBanDen, on_delete=models.CASCADE, null=True, blank=True)
   VanBanDi = models.ForeignKey(VanBanDi, on_delete=models.CASCADE, null=True, blank=True)


   TrangThai = models.CharField(
       max_length=50,
       choices=TrangThaiCongViec.choices,
       default=TrangThaiCongViec.CHO_XET_DUYET
   )


   def __str__(self):
       return f"{self.TieuDe} → {self.NguoiNhan}"


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
   PhanCong = models.ForeignKey(PhanCongCongViec, on_delete=models.CASCADE, related_name='nhatky', null=True, blank=True)
   ThoiGian = models.DateTimeField(auto_now_add=True)
   ThaoTac = models.TextField("Thao tác")
   TrangThai = models.CharField(max_length=50, choices=TrangThaiCongViec.choices)
   NguoiThucHien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người thực hiện")


   def __str__(self):
       pc = self.PhanCong.TieuDe if self.PhanCong else "N/A"
       return f"{pc} - {self.get_TrangThai_display()}"

# QLVB/constants.py
from django.db import models




class TrangThaiCongViec(models.TextChoices):
   CHO_XET_DUYET = "Chờ xét duyệt", "CHỜ XÉT DUYỆT"
   BI_TU_CHOI = "Bị từ chối", "BỊ TỪ CHỐI"
   CHO_PHAN_CONG = "Chờ phân công", "CHỜ PHÂN CÔNG"
   CHO_XAC_NHAN = "Chờ xác nhận", "CHỜ XÁC NHẬN"
   DANG_XU_LY = "Đang xử lý", "ĐANG XỬ LÝ"
   HOAN_THANH = "Hoàn thành", "HOÀN THÀNH"
   CHO_BAN_HANH = "Chờ ban hành", "CHỜ BAN HÀNH"
   DA_BAN_HANH = "Đã ban hành", "ĐÃ BAN HÀNH"


