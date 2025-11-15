# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'ho_ten', 'email', 'sdt', 'vai_tro', 'ma_phong_ban', 'is_staff')
    search_fields = ('username', 'ho_ten', 'email', 'sdt')
    list_filter = ('vai_tro', 'ma_phong_ban', 'is_staff', 'is_active', 'date_joined')

    # SỬA: LOẠI BỎ 'email' vì đã có trong BaseUserAdmin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin nhân viên', {
            'fields': ('ho_ten', 'sdt', 'vai_tro', 'ma_phong_ban')  # XÓA 'email'
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Thông tin nhân viên', {
            'fields': ('ho_ten', 'sdt', 'vai_tro', 'ma_phong_ban')  # XÓA 'email'
        }),
    )