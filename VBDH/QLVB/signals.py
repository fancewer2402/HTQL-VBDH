from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import VanBanDen, VanBanDi, ThongBao
from .models import VanBanDi, VanBanDen, ThongBao, PhongBan
from accounts.models import User as NhanVien


# --- VĂN BẢN ĐẾN ---

@receiver(post_save, sender=VanBanDen)
def create_notification_for_vbden(sender, instance, created, **kwargs):
    """Tạo thông báo tự động cho văn bản đến khi mới được thêm."""
    if created:
        # Gửi thông báo tới Quản lý để xét duyệt
        quan_ly_group = NhanVien.objects.filter(VaiTro='QL')
        for nv in quan_ly_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đến [{instance.SoHieu}] đang chờ xét duyệt.",
                NoiDung=f"Văn bản '{instance.TrichYeu}' vừa được gửi đến và cần xét duyệt.",
                MaNhanVien=nv,
                MaVBDen=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )


@receiver(post_save, sender=VanBanDen)
def notify_vanthu_after_approval(sender, instance, **kwargs):
    """Gửi thông báo tới Văn thư khi Quản lý phê duyệt hoặc không phê duyệt."""
    if hasattr(instance, "TrangThai") and instance.TrangThai == "Đã phê duyệt":
        van_thu_group = NhanVien.objects.filter(VaiTro='VT')
        for nv in van_thu_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đến [{instance.SoHieu}] đã được Quản lý phê duyệt.",
                NoiDung=f"Văn bản '{instance.TrichYeu}' đã được phê duyệt, chuẩn bị xử lý tiếp.",
                MaNhanVien=nv,
                MaVBDen=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )
    elif instance.TrangThai == "Không phê duyệt":
        van_thu_group = NhanVien.objects.filter(VaiTro='VT')
        for nv in van_thu_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đến [{instance.SoHieu}] không được Quản lý phê duyệt.",
                NoiDung=f"Văn bản '{instance.TrichYeu}' bị từ chối. Vui lòng xem lại.",
                MaNhanVien=nv,
                MaVBDen=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )


@receiver(post_save, sender=VanBanDen)
def notify_nhanvien_assignment(sender, instance, **kwargs):
    """Gửi thông báo cho nhân viên khi được phân công xử lý."""
    if hasattr(instance, 'NhanVienXuLy') and instance.NhanVienXuLy:
        ThongBao.objects.create(
            TieuDe=f"Bạn được phân công xử lý văn bản đến [{instance.SoHieu}].",
            NoiDung=f"Vui lòng xử lý văn bản '{instance.TrichYeu}' đúng thời hạn.",
            MaNhanVien=instance.NhanVienXuLy,
            MaVBDen=instance,
            NgayTao=timezone.now(),
            DaDoc=False
        )


@receiver(post_save, sender=VanBanDen)
def notify_quanly_after_done(sender, instance, **kwargs):
    """Gửi thông báo tới Quản lý khi nhân viên hoàn thành xử lý văn bản."""
    if instance.TrangThai == "Hoàn thành":
        quan_ly_group = NhanVien.objects.filter(VaiTro='QL')
        for nv in quan_ly_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đến [{instance.SoHieu}] đã hoàn thành xử lý.",
                NoiDung=f"Văn bản '{instance.TrichYeu}' đã được nhân viên xử lý xong.",
                MaNhanVien=nv,
                MaVBDen=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )

# --- VĂN BẢN ĐI ---

@receiver(post_save, sender=VanBanDi)
def notify_vanthu_for_vbdi(sender, instance, created, **kwargs):
    """Thông báo khi văn bản đi được phân công xử lý tới Văn thư."""
    if hasattr(instance, 'NhanVienXuLy') and instance.NhanVienXuLy:
        ThongBao.objects.create(
            TieuDe=f"Bạn được phân công xử lý văn bản đi '{instance.TieuDe}'.",
            NoiDung=f"Văn bản đi '{instance.TieuDe}' vừa được giao cho bạn xử lý.",
            MaNhanVien=instance.NhanVienXuLy,
            MaVBDi=instance,
            NgayTao=timezone.now(),
            DaDoc=False
        )


@receiver(post_save, sender=VanBanDi)
def notify_quanly_vbdi_ban_hanh(sender, instance, **kwargs):
    """Thông báo cho Quản lý khi văn bản đi đã được ký số và ban hành."""
    if instance.TrangThai == "Đã ban hành":
        quan_ly_group = NhanVien.objects.filter(VaiTro='QL')
        for nv in quan_ly_group:
            ThongBao.objects.create(
                TieuDe=f"Văn bản đi '{instance.TieuDe}' đã được ký số và ban hành.",
                NoiDung=f"Văn bản đi '{instance.TieuDe}' đã hoàn tất quy trình ban hành.",
                MaNhanVien=nv,
                MaVBDi=instance,
                NgayTao=timezone.now(),
                DaDoc=False
            )
