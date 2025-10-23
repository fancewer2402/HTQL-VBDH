from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import VanBanDi, VanBanDen, NhanVien
from datetime import date
from .models import VanBanDi, VanBanDen
from django.utils import timezone
from django.utils import timezone
from datetime import timedelta

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Giả sử bạn phân quyền theo nhóm:
            if user.groups.filter(name='Quản lý').exists():
                return redirect('dashboard_quanly')
            elif user.groups.filter(name='Văn thư').exists():
                return redirect('dashboard_vanthu')
            else:
                return redirect('dashboard_nhanvien')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
    return render(request, 'QLVB/login.html')

def tra_cuu_van_ban(request):
    return render(request, 'QLVB/tra_cuu_van_ban.html')

def them_van_ban(request):
    return render(request, 'vanbanden/create.html')

def ds_vanbandi(request):
    ds = VanBanDi.objects.all().order_by('-NgayBanHanh')
    return render(request, 'vanbandi/vanbandi.html', {'ds_vanbandi': ds})

def vanbandi_detail(request, pk):
    vb = get_object_or_404(VanBanDi, pk=pk)
    return render(request, 'vanbandi/vanbandi_detail.html', {'vb': vb})

def get_current_nhanvien(request):
    # Nếu bạn chưa map user -> NhanVien, trả về None (đổi logic nếu cần)
    try:
        email = request.user.email
        return NhanVien.objects.filter(Email=email).first()
    except Exception:
        return None

def danh_sach_van_ban_den(request):
    van_ban_list = VanBanDen.objects.all().order_by('-NgayDen')
    paginator = Paginator(van_ban_list, 10)  # mỗi trang 10 văn bản
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'vanbanden/danh_sach_van_ban_den.html', {
        'van_ban_list': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
    })

# def chi_tiet_van_ban_den(request, id):
#     vb = get_object_or_404(VanBanDen, id=id)
#     return render(request, 'QLVB/chi_tiet_vb_den.html', {'vb': vb})

def chi_tiet_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    vb_truoc = VanBanDen.objects.filter(id__lt=vb.id).order_by('-id').first()
    vb_sau = VanBanDen.objects.filter(id__gt=vb.id).order_by('id').first()
    return render(request, 'vanbanden/chi_tiet_vb_den.html', {
        'vb': vb,
        'vb_truoc': vb_truoc,
        'vb_sau': vb_sau
    })

def tao_du_thao(request):
    # Trả về template taoduthao.html
    return render(request, 'vanbandi/tao_du_thao.html')

def ban_hanh_van_ban(request, id):
    vb = get_object_or_404(VanBanDi, id=id)
    today = timezone.now().date()   # Lấy ngày hiện tại (chỉ phần ngày, không có giờ)

    context = {
        'vb': vb,
        'today': today
    }
    return render(request, 'vanbandi/ban_hanh_van_ban.html', context)

from .models import ThongBao

def home(request):
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())  # Thứ 2 của tuần

    today_notifications = ThongBao.objects.filter(NgayTao__date=now.date())
    week_notifications = ThongBao.objects.filter(
        NgayTao__gte=start_of_week,
        NgayTao__lt=now.date()
    )
    old_notifications = ThongBao.objects.filter(NgayTao__lt=start_of_week)

    notification_count = ThongBao.objects.count()

    context = {
        'today_notifications': today_notifications,
        'week_notifications': week_notifications,
        'old_notifications': old_notifications,
        'notification_count': notification_count,
    }
    return render(request, 'home.html', context)

def global_notifications(request):
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())

    today_notifications = ThongBao.objects.filter(NgayTao__date=now.date())
    week_notifications = ThongBao.objects.filter(NgayTao__gte=start_of_week, NgayTao__lt=now.date())
    old_notifications = ThongBao.objects.filter(NgayTao__lt=start_of_week)

    return {
        'today_notifications': today_notifications,
        'week_notifications': week_notifications,
        'old_notifications': old_notifications,
        'notification_count': ThongBao.objects.count()
    }

def mark_notification_read(request, id):
    thongbao = get_object_or_404(ThongBao, id=id)
    thongbao.DaDoc = True
    thongbao.save()
    next_url = request.GET.get('next', '/')
    return redirect(next_url)