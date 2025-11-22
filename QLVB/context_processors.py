from datetime import timedelta
from django.utils import timezone
from .models import ThongBao
from accounts.models import User as NhanVien


def thong_bao_context(request):
    today_notifications = []
    week_notifications = []
    old_notifications = []
    notification_count = 0

    if request.user.is_authenticated:
        try:
            nhanvien = NhanVien.objects.get(email=request.user.email)
            all_thong_baos = ThongBao.objects.filter(MaNhanVien=nhanvien).order_by('-NgayTao')

            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())

            for tb in all_thong_baos:
                tb_date = tb.NgayTao.date()
                # Tạo URL chi tiết cho VB đến hoặc đi
                if tb.MaVBDen:
                    url = f"/vanbanden/{tb.MaVBDen.id}/"
                elif tb.MaVBDi:
                    url = f"/vanbandi/{tb.MaVBDi.id}/"
                else:
                    url = "/"

                item = {
                    'TieuDe': tb.TieuDe,
                    'url': url,
                    'DaDoc': tb.DaDoc,
                    'id': tb.id
                }

                if tb_date == today:
                    today_notifications.append(item)
                elif week_start <= tb_date < today:
                    week_notifications.append(item)
                else:
                    old_notifications.append(item)

            notification_count = all_thong_baos.filter(DaDoc=False).count()

        except NhanVien.DoesNotExist:
            pass

    return {
        'today_notifications': today_notifications,
        'week_notifications': week_notifications,
        'old_notifications': old_notifications,
        'notification_count': notification_count
    }
