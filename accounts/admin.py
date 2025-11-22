# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from .models import User


# Form thêm user mới có kiểm tra trùng email
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'ho_ten', 'sdt', 'vai_tro', 'ma_phong_ban')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email này đã được sử dụng. Vui lòng chọn email khác.")
        return email


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'ho_ten', 'email', 'sdt', 'vai_tro', 'ma_phong_ban', 'is_staff')
    search_fields = ('username', 'ho_ten', 'email', 'sdt')
    list_filter = ('vai_tro', 'ma_phong_ban', 'is_staff', 'is_active', 'date_joined')
    ordering = ('username',)

    # Form khi thêm user mới
    add_form = CustomUserCreationForm

    # Khi sửa user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('ho_ten', 'email', 'sdt')}),
        ('Phân quyền', {'fields': ('vai_tro', 'ma_phong_ban')}),
        ('Quyền hệ thống', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Ngày quan trọng', {'fields': ('last_login', 'date_joined')}),
    )

    # QUAN TRỌNG: Khi thêm user mới phải có email và password1, password2
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Thông tin nhân viên', {
            'classes': ('wide',),
            'fields': ('ho_ten', 'sdt', 'vai_tro', 'ma_phong_ban'),
        }),
    )

    # Sắp xếp và hiển thị
    filter_horizontal = ('groups', 'user_permissions',)