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
