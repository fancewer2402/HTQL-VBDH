from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'ho_ten', 'email', 'sdt', 'vai_tro', 'ma_phong_ban', 'is_staff')
    search_fields = ('username', 'ho_ten', 'email', 'sdt')
    list_filter = ('vai_tro', 'ma_phong_ban', 'is_staff', 'is_active', 'date_joined')

    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
        }),
        ('Thông tin nhân viên', {
            'fields': ('ho_ten', 'email', 'sdt', 'ma_phong_ban'),
        }),
        ('Quyền hệ thống', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups'
            ),
        }),
        ('Thông tin hệ thống', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'ho_ten',
                'sdt',
                'email',
                'vai_tro',
                'ma_phong_ban'
            ),
        }),
    )
