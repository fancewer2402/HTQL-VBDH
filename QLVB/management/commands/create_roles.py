# accounts/management/commands/create_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

class Command(BaseCommand):
    help = "Tạo nhóm (roles) và gán permission cơ bản"

    def handle(self, *args, **options):
        # tên nhóm
        roles = ["NhanVien", "VanThu", "QuanLy", "TruongPhong"]
        # tạo nhóm nếu chưa tồn tại
        for r in roles:
            Group.objects.get_or_create(name=r)

        # Lấy permissions mẫu (ví dụ: model-level cho PhongBan và User)
        PhongBan = apps.get_model('accounts', 'PhongBan')
        User = apps.get_model('accounts', 'User')

        # ví dụ gán quyền: VanThu -> xu_ly_van_thu
        p_van_thu = Permission.objects.filter(codename='xu_ly_van_thu').first()
        p_quan_ly = Permission.objects.filter(codename='quan_ly_nhan_su').first()
        p_phe_duyet = Permission.objects.filter(codename='phe_duyet').first()

        # gán
        if p_van_thu:
            Group.objects.get(name='VanThu').permissions.add(p_van_thu)
        if p_quan_ly:
            Group.objects.get(name='QuanLy').permissions.add(p_quan_ly)
        if p_phe_duyet:
            Group.objects.get(name='TruongPhong').permissions.add(p_phe_duyet)

        # ví dụ thêm permission cơ bản: QuanLy + TruongPhong có quyền change/delete user
        for codename in ['change_user', 'delete_user', 'view_user', 'change_phongban', 'view_phongban']:
            perm = Permission.objects.filter(codename=codename).first()
            if perm:
                Group.objects.get(name='QuanLy').permissions.add(perm)
                Group.objects.get(name='TruongPhong').permissions.add(perm)

        self.stdout.write(self.style.SUCCESS("Đã tạo roles và gán permission cơ bản."))
