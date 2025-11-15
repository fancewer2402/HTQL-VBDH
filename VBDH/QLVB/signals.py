from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import VanBanDen, VanBanDi, ThongBao
from accounts.models import User as NhanVien


# =========================================
#               VĂN BẢN ĐẾN
# =========================================

@receiver(post_save, sender=VanBanDen)
def create_notification_for_vbden(sender, instance, created, **kwargs):
    """Tạo thông báo khi có văn bản đến mới (chờ xét duyệt)."""
    if created:
        quan_ly_group = NhanVien.objects.filter(vai_tro='QL')
        for nv in quan_ly_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đến [{instance.SoHieu}] đang chờ xét duyệt",
                NoiDung=f"Văn bản '{instance.TrichYeu}' cần được Quản lý phê duyệt.",
                MaNhanVien=nv,
                MaVBDen=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )


@receiver(post_save, sender=VanBanDen)
def notify_vanthu_after_approval(sender, instance, **kwargs):
    """Thông báo Văn thư khi Quản lý phê duyệt / từ chối."""
    if not hasattr(instance, 'TrangThai'):
        return

    van_thu_group = NhanVien.objects.filter(vai_tro='VT')

    if instance.TrangThai == "Đã phê duyệt":
        for nv in van_thu_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đến [{instance.SoHieu}] đã được phê duyệt",
                NoiDung=f"Văn bản '{instance.TrichYeu}' đã được duyệt. Vui lòng xử lý tiếp.",
                MaNhanVien=nv,
                MaVBDen=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )

    elif instance.TrangThai == "Không phê duyệt":
        for nv in van_thu_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đến [{instance.SoHieu}] bị từ chối",
                NoiDung=f"Văn bản '{instance.TrichYeu}' không được duyệt. Vui lòng kiểm tra lại.",
                MaNhanVien=nv,
                MaVBDen=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )


@receiver(post_save, sender=VanBanDen)
def notify_nhanvien_assignment(sender, instance, **kwargs):
    """Thông báo nhân viên khi được phân công xử lý."""
    # Kiểm tra nếu model có field NhanVienXuLy
    if hasattr(instance, 'NhanVienXuLy') and instance.NhanVienXuLy:
        ThongBao.objects.create(
            TieuDe=f"Bạn được phân công xử lý văn bản đến [{instance.SoHieu}]",
            NoiDung=f"Vui lòng xử lý văn bản '{instance.TrichYeu}' đúng hạn.",
            MaNhanVien=instance.NhanVienXuLy,
            MaVBDen=instance,
            NgayTao=timezone.now(),
            DaDoc=False
        )


@receiver(post_save, sender=VanBanDen)
def notify_quanly_after_done(sender, instance, **kwargs):
    """Thông báo Quản lý khi nhân viên hoàn thành xử lý."""
    if instance.TrangThai == "Hoàn thành":
        quan_ly_group = NhanVien.objects.filter(vai_tro='QL')
        for nv in quan_ly_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đến [{instance.SoHieu}] đã hoàn thành",
                NoiDung=f"Nhân viên đã xử lý xong văn bản '{instance.TrichYeu}'.",
                MaNhanVien=nv,
                MaVBDen=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )


# =========================================
#               VĂN BẢN ĐI
# =========================================

@receiver(post_save, sender=VanBanDi)
def notify_vanthu_for_vbdi(sender, instance, **kwargs):
    """Thông báo Văn thư khi được phân công soạn thảo văn bản đi."""
    # SỬA: Kiểm tra nếu model có field NhanVienXuLy (nếu không có thì bỏ qua)
    if hasattr(instance, 'NhanVienXuLy') and instance.NhanVienXuLy:
        ThongBao.objects.create(
            TieuDe=f"Bạn được phân công soạn thảo văn bản đi [{instance.SoHieu}]",
            NoiDung=f"Vui lòng soạn thảo văn bản '{instance.TrichYeu}'.",
            MaNhanVien=instance.NhanVienXuLy,
            MaVBDi=instance,
            NgayTao=timezone.now(),
            DaDoc=False
        )


@receiver(post_save, sender=VanBanDi)
def notify_quanly_vbdi_ban_hanh(sender, instance, **kwargs):
    """Thông báo Quản lý khi văn bản đi được ban hành."""
    if instance.TrangThai == "Đã ban hành":
        quan_ly_group = NhanVien.objects.filter(vai_tro='QL')
        for nv in quan_ly_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đi [{instance.SoHieu}] đã được ban hành",
                NoiDung=f"Văn bản '{instance.TrichYeu}' đã hoàn tất ban hành và gửi đi.",
                MaNhanVien=nv,
                MaVBDi=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )