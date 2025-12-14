from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
   help = "Tạo 4 nhóm quyền và gán chính xác theo bảng phân quyền chính thức (tự động thay thế tick tay)"


   def handle(self, *args, **options):
       # ==============================================================
       # PHÂN QUYỀN ĐÚNG THEO HƯỚNG DẪN CHI TIẾT BẠN GỬI
       # ==============================================================
       groups_permissions = {
           # ====================== 1. NHÂN VIÊN ======================
           "Nhân viên": [
               # Văn bản đến
               "xemchitiet_vanbanden",
               "xemdanhsach_vanbanden",
               "capnhat_trangthai_cv_vbden",
               "xem_nhatky_vanbanden",
               # Văn bản đi / dự thảo
               "tao_vanbandi",
               "sua_vanbandi",
               "xemchitiet_vanbandi",
               "xemdanhsach_vanbandi",
               # Chung
               "tracuu_hethong",
               "xem_thongbao",
           ],


           # ====================== 2. VĂN THƯ ======================
           "Văn thư": [
               # Văn bản đến
               "tao_vanbanden",
               "sua_vanbanden",
               "xemchitiet_vanbanden",
               "xemdanhsach_vanbanden",
               "xem_nhatky_vanbanden",
               # Văn bản đi / dự thảo
               "tao_vanbandi",           # Văn thư cũng được soạn (thường có)
               "sua_vanbandi",
               "xemchitiet_vanbandi",
               "xemdanhsach_vanbandi",
               "banhanh_vanbandi",
               # Chung
               "tracuu_hethong",
               "xem_thongbao",
           ],


           # ====================== 3. TRƯỞNG PHÒNG ======================
           "Trưởng phòng": [
               # Văn bản đến
               "phancong_vanbanden",
               "xemchitiet_vanbanden",
               "xemdanhsach_vanbanden",
               # Văn bản đi / dự thảo
               "thongqua_vanbandi",
               "phancong_vanbandi",
               "xemchitiet_vanbandi",
               "xemdanhsach_vanbandi",
               # Chung
               "tracuu_hethong",
               "xem_thongbao",
               "xem_nhatky_vanbanden",
           ],


           # ====================== 4. QUẢN LÝ (LÃNH ĐẠO) ======================
           "Quản lý": [
               # Văn bản đến
               "xetduyet_vanbanden",
               "phancong_vanbanden",
               "xemchitiet_vanbanden",
               "xemdanhsach_vanbanden",
               "xem_nhatky_vanbanden",
               # Văn bản đi / dự thảo
               "xetduyet_vanbandi",
               "phancong_vanbandi",
               "xemchitiet_vanbandi",
               "xemdanhsach_vanbandi",
               # Chung
               "tracuu_hethong",
               "xem_thongbao",
           ],
       }


       total_added = 0
       for group_name, codenames in groups_permissions.items():
           group, created = Group.objects.get_or_create(name=group_name)
           if created:
               self.stdout.write(self.style.SUCCESS(f"✓ Tạo mới nhóm: {group_name}"))


           # Lấy permission theo codename
           perms = Permission.objects.filter(codename__in=codenames)
           current = set(group.permissions.values_list('codename', flat=True))
           missing = set(codenames) - current


           if missing:
               group.permissions.add(*perms.filter(codename__in=missing))
               total_added += len(missing)
               self.stdout.write(self.style.WARNING(f"→ Gán thêm {len(missing)} quyền cho nhóm '{group_name}'"))
           else:
               self.stdout.write(f"Nhóm '{group_name}' đã đúng quyền.")


       self.stdout.write(
           self.style.SUCCESS(
               f"\nHOÀN TẤT! Đã tạo/gán quyền cho 4 nhóm: Nhân viên, Văn thư, Trưởng phòng, Quản lý\n"
               f"→ Tổng cộng thêm {total_added} quyền theo đúng hướng dẫn tick tay.\n"
               f"Chạy lại lệnh này bất kỳ lúc nào cũng an toàn!"
           )
       )

