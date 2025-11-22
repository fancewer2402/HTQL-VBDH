# QLVB/admin.py
from django.contrib import admin
from .models import (
    PhongBan, VanBanDen, VanBanDi,
    ThongBao, PhanCongCongViec, NhatKyCongViec
)

# Đăng ký các model ở đây...
@admin.register(PhongBan)
class PhongBanAdmin(admin.ModelAdmin):
    list_display = ('TenPhongBan', 'Email')
    search_fields = ('TenPhongBan', 'Email')

# ... các model khác