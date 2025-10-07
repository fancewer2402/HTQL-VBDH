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


class VanBanDi(models.Model):
    id = models.AutoField(primary_key=True)  # ID
    so_hieu = models.CharField(max_length=50, unique=True)  # SoHieu
    ngay_ban_hanh = models.DateField(null=True, blank=True)  # NgayBanHanh
    trich_yeu = models.CharField(max_length=255)  # TrichYeu
    noi_dung = models.TextField()  # NoiDung
    loai_vb_di = models.CharField(max_length=255)  # LoaiVbDi
    don_vi_nhan = models.CharField(max_length=255, null=True, blank=True)  # DonViNhan
    file_dinh_kem = models.CharField(max_length=255, null=True, blank=True)  # DinhKem
    do_mat = models.CharField(max_length=255, null=True, blank=True)  # DoMat
    do_khan = models.CharField(max_length=255, null=True, blank=True)  # DoKhan
    trang_thai = models.CharField(max_length=255, null=True, blank=True)  # TrangThai
    ngay_tao = models.DateTimeField(auto_now_add=True)  # NgayTao
    ma_nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)  # MaNhanVien

    def __str__(self):
        return self.trich_yeu
