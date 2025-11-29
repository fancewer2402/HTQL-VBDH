# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ho_ten = models.CharField("Họ tên", max_length=100, blank=True, null=True)
    sdt = models.CharField("Số điện thoại", max_length=15, blank=True, null=True)

    # ĐÃ SỬA: default='' + null=False → SQLite không còn lỗi UNIQUE với NULL nữa
    email = models.EmailField(
        "Email",
        unique=True,
        blank=True,
        null=False,  # quan trọng
        default=''  # quan trọng nhất
    )

    VAITRO_CHOICES = [
        ('NV', 'Nhân Viên'),
        ('QL', 'Quản Lý'),
        ('VT', 'Văn Thư'),
        ('TP', 'Trưởng Phòng'),
    ]
    vai_tro = models.CharField(
        "Vai trò", max_length=2, choices=VAITRO_CHOICES, blank=True, null=True
    )

    # ĐÃ SỬA: dùng string 'QLVB.PhongBan' để tránh Circular Dependency
    ma_phong_ban = models.ForeignKey(
        'QLVB.PhongBan',  # ← sửa thành chuỗi
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nhan_viens',
        verbose_name="Phòng ban"
    )

    def __str__(self):
        return self.ho_ten or self.username or self.email or ""

    class Meta:
        verbose_name = "Nhân viên"
        verbose_name_plural = "Nhân viên"  # đã bỏ dấu chấm thừa