from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import VanBanDi, VanBanDen, ThongBao, NhatKyCongViec, PhongBan
from datetime import timedelta, datetime, date
from django.utils import timezone
from accounts.models import User as NhanVien
from django.contrib.auth.decorators import login_required

# Đăng nhập
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('danh_sach_van_ban_den')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")

    return render(request, 'QLVB/login.html')

# Đăng xuất
@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return redirect('login')

def tra_cuu_van_ban(request):
    return render(request, 'QLVB/tra_cuu_van_ban.html')

@login_required(login_url='/login/')
def them_van_ban(request):
    return render(request, 'vanbanden/create.html')

@login_required(login_url='/login/')
def ds_vanbandi(request):
    ds = VanBanDi.objects.all().order_by('-NgayBanHanh')
    return render(request, 'vanbandi/vanbandi.html', {'ds_vanbandi': ds})

@login_required(login_url='/login/')
def vanbandi_detail(request, pk):
    vb = get_object_or_404(VanBanDi, pk=pk)
    return render(request, 'vanbandi/vanbandi_detail.html', {'vb': vb})

@login_required(login_url='/login/')
def sua_vanbandi(request, id):
    vb = get_object_or_404(VanBanDi, id=id)
    if request.method == 'POST':
        vb.TrichYeu = request.POST.get('TrichYeu')
        vb.SoKyHieu = request.POST.get('SoKyHieu')
        vb.NoiDung = request.POST.get('NoiDung')
        vb.save()
        return redirect('vanbandi_detail', pk=vb.id)
    return render(request, 'vanbandi/sua_vanbandi.html', {'vb': vb})

@login_required(login_url='/login/')
def get_current_nhanvien(request):
    try:
        email = request.user.email
        return NhanVien.objects.filter(email=email).first()
    except Exception:
        return None

@login_required(login_url='/login/')
def danh_sach_van_ban_den(request):
    van_ban_list = VanBanDen.objects.all().order_by('-NgayDen')
    paginator = Paginator(van_ban_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'vanbanden/danh_sach_van_ban_den.html', {
        'van_ban_list': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
    })

@login_required(login_url='/login/')
def chi_tiet_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    vb_truoc = VanBanDen.objects.filter(id__lt=vb.id).order_by('-id').first()
    vb_sau = VanBanDen.objects.filter(id__gt=vb.id).order_by('id').first()
    total_vb = VanBanDen.objects.count()
    return render(request, 'vanbanden/chi_tiet_vb_den.html', {
        'vb': vb,
        'vb_truoc': vb_truoc,
        'vb_sau': vb_sau,
        'total_vb': total_vb
    })

@login_required(login_url='/login/')
def tao_du_thao(request):
    return render(request, 'vanbandi/tao_du_thao.html')

@login_required(login_url='/login/')
def xetduyetvanbandi(request, id):
    vb = get_object_or_404(VanBanDi, id=id)
    if request.method == "POST":
        if 'duyet' in request.POST:
            vb.trang_thai = "Đã duyệt"
            vb.save()
            return redirect('phancong_vanthu', id=vb.id)
    return render(request, 'vanbandi/xetduyetvanbandi.html', {'vb': vb})

@login_required(login_url='/login/')
def phan_cong_van_thu(request, id):
    vb = get_object_or_404(VanBanDi, id=id)
    return render(request, 'vanbandi/phan_cong_van_thu.html', {'vb': vb})

@login_required(login_url='/login/')
def nhat_ky_hoat_dong(request, loaivanban, vanban_id):
    if loaivanban == 'vanbanden':
        vanban = get_object_or_404(VanBanDen, id=vanban_id)
        nhatky = NhatKyCongViec.objects.filter(MaVBDen=vanban).order_by('NgayTao')
    elif loaivanban == 'vanbandi':
        vanban = get_object_or_404(VanBanDi, id=vanban_id)
        nhatky = NhatKyCongViec.objects.filter(MaVBDi=vanban).order_by('NgayTao')
    else:
        nhatky = []
        vanban = None
    context = {
        'loaivanban': loaivanban,
        'vanban': vanban,
        'nhatky': nhatky,
    }
    return render(request, 'QLVB/nhat_ky_hoat_dong.html', context)

@login_required(login_url='/login/')
def ban_hanh_van_ban(request, id):
    vb = get_object_or_404(VanBanDi, id=id)
    today = timezone.now().date()
    context = {
        'vb': vb,
        'today': today
    }
    return render(request, 'vanbandi/ban_hanh_van_ban.html', context)

@login_required(login_url='/login/')
def home(request):
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())
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

@login_required(login_url='/login/')
def mark_notification_read(request, id):
    thongbao = get_object_or_404(ThongBao, id=id)
    thongbao.DaDoc = True
    thongbao.save()
    next_url = request.GET.get('next', '/')
    return redirect(next_url)

@login_required(login_url='/login/')
def xet_duyet_vb_den(request, vb_id):
    vanbanden = get_object_or_404(VanBanDen, id=vb_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            vanbanden.TrangThai = "Chờ phân công"
            vanbanden.save()
            return redirect('phan_cong_nhan_vien_vbden', id=vanbanden.pk)
        elif action == 'reject':
            vanbanden.TrangThai = "Từ chối"
            vanbanden.save()
            return redirect('danh_sach_van_ban_den')
    return render(request, 'vanbanden/xetduyet_vanbanden.html', {'vb': vanbanden})

@login_required(login_url='/login/')
def phan_cong_nhan_vien_vbden(request, id):
    vb = get_object_or_404(VanBanDen, id=id)
    nhanviens = NhanVien.objects.filter(MaPhongBan=vb.MaPhongBan)
    if request.method == "POST":
        ma_nhanvien_id = request.POST.get("MaNhanVien")
        tieude = request.POST.get("TieuDe")
        mota = request.POST.get("MoTa")
        han_chot = request.POST.get("HanChot")
        thao_tac = request.POST.get("ThaoTac")
        if not all([ma_nhanvien_id, tieude, mota, han_chot, thao_tac]):
            messages.error(request, "⚠️ Vui lòng nhập đầy đủ thông tin trước khi lưu.")
        else:
            nhanvien = get_object_or_404(NhanVien, id=ma_nhanvien_id)
            NhatKyCongViec.objects.create(
                MaVBDen=vb,
                MaNhanVien=nhanvien,
                TieuDe=tieude,
                MoTa=mota,
                HanChot=han_chot,
                ThaoTac=thao_tac,
                TrangThai=NhatKyCongViec.TrangThai.ChoXacNhan,
            )
            vb.TrangThai = "Chờ xác nhận"
            vb.save()
            messages.success(request, f"✅ Đã phân công xử lý văn bản cho {nhanvien.HoTen}.")
            return redirect("danh_sach_van_ban_den")
    context = {
        "vb": vb,
        "nhanviens": nhanviens,
    }
    return render(request, "vanbanden/phancong_vanbanden.html", context)

@login_required(login_url='/login/')
def xac_nhan_phan_cong_vbden(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    nhanvien = getattr(request.user, "nhanvien", None)
    nhatky = NhatKyCongViec.objects.filter(MaVBDen=vb, MaNhanVien=nhanvien).last()
    if request.method == "POST":
        if request.POST.get("action") == "confirm":
            if nhatky:
                nhatky.TrangThai = NhatKyCongViec.TrangThai.DangXuLy
                nhatky.save()
            vb.TrangThai = "Chờ xử lý"
            vb.save()
            messages.success(request, "✅ Đã xác nhận xử lý văn bản đến.")
            return redirect("bao_cao_vbden", vb_id=vb.id)
    context = {
        "vb": vb,
        "nhanvien": nhanvien,
    }
    return render(request, "vanbanden/xacnhan_phancong_vbden.html", context)

@login_required(login_url='/login/')
def bao_cao_vbden(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    if request.method == "POST":
        vb.TrangThai = "Hoàn thành"
        vb.save()
        messages.success(request, f"✅ Văn bản '{vb.TrichYeu}' đã được đánh dấu là Hoàn thành.")
        return redirect('danh_sach_van_ban_den')
    return render(request, "vanbanden/baocao_vbden.html", {"vb": vb})

@login_required(login_url='/login/')
def sua_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    phongbans = PhongBan.objects.all()
    if request.method == 'POST':
        vb.SoHieu = request.POST.get('SoHieu')
        vb.TrichYeu = request.POST.get('TrichYeu')
        vb.LoaiVBDen = request.POST.get('LoaiVBDen')
        vb.DonViPhatHanh = request.POST.get('DonViPhatHanh')
        ngay_bh = request.POST.get('NgayBanHanh')
        ngay_den = request.POST.get('NgayDen')
        try:
            vb.NgayBanHanh = datetime.strptime(ngay_bh, '%Y-%m-%d')
        except (TypeError, ValueError):
            vb.NgayBanHanh = vb.NgayBanHanh
        try:
            vb.NgayDen = datetime.strptime(ngay_den, '%Y-%m-%d')
        except (TypeError, ValueError):
            vb.NgayDen = vb.NgayDen

        vb.DoKhan = request.POST.get('DoKhan', vb.DoKhan)
        vb.DoMat = request.POST.get('DoMat', vb.DoMat)
        phongban_id = request.POST.get('MaPhongBan')
        if phongban_id:
            try:
                vb.MaPhongBan = PhongBan.objects.get(id=int(phongban_id))
            except (PhongBan.DoesNotExist, ValueError):
                pass
        vb.NoiDung = request.POST.get('NoiDung', vb.NoiDung)
        vb.save()
        return redirect('chi_tiet_vb_den', vb_id=vb.id)
    return render(request, 'vanbanden/sua_van_ban_den.html', {
        'vb': vb,
        'phongbans': phongbans,
    })
