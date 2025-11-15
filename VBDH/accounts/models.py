from django.contrib.auth.models import AbstractUser
from django.db import models
from QLVB.models import PhongBan

class User(AbstractUser):
    ho_ten = models.CharField("Họ tên", max_length=100, blank=True, null=True)
    sdt = models.CharField("Số điện thoại", max_length=15, blank=True, null=True)
    email = models.EmailField("Email", unique=True, blank=True, null=True)

    VAITRO_CHOICES = [
        ('NV', 'Nhân Viên'), ('QL', 'Quản Lý'),
        ('VT', 'Văn Thư'), ('TP', 'Trưởng Phòng'),
    ]
    vai_tro = models.CharField("Vai trò", max_length=2, choices=VAITRO_CHOICES, blank=True, null=True)
    ma_phong_ban = models.ForeignKey(
        PhongBan, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='nhan_viens', verbose_name="Phòng ban"
    )

    def __str__(self):
        return self.ho_ten or self.username or self.email

    class Meta:
        verbose_name = "Nhân viên"
        verbose_name_plural = "Nhân viên"