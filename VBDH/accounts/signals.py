from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def add_user_to_group(sender, instance, created, **kwargs):
    if not instance.vai_tro:
        return

    # Map vai trò → tên group
    role_group_map = {
        'NV': 'NhanVien',
        'QL': 'QuanLy',
        'VT': 'VanThu',
        'TP': 'TruongPhong',
    }

    group_name = role_group_map.get(instance.vai_tro)
    if not group_name:
        return

    try:
        group = Group.objects.get(name=group_name)

        # Xóa group cũ để tránh trùng
        instance.groups.clear()

        # Thêm group mới
        instance.groups.add(group)

    except Group.DoesNotExist:
        print(f"[WARNING] Group '{group_name}' chưa tồn tại.")
