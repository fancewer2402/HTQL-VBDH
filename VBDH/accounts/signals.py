from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings

from .models import User


ROLE_GROUP_MAP = {
    'NV': 'Nhân viên',
    'VT': 'Văn thư',
    'TP': 'Trưởng phòng',
    'QL': 'Quản lý',
}


@receiver(post_save, sender=User)
def sync_user_group(sender, instance, created, **kwargs):
    role = instance.vai_tro
    if not role:
        return

    group_name = ROLE_GROUP_MAP.get(role)
    if not group_name:
        return

    group, _ = Group.objects.get_or_create(name=group_name)

    # Xóa toàn bộ group cũ (nếu muốn mỗi user chỉ thuộc 1 group)
    instance.groups.clear()

    # Thêm group mới
    instance.groups.add(group)
