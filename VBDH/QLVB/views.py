from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import VanBanDi, VanBanDen, NhanVien


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
    total_vb = VanBanDen.objects.count()
    return render(request, 'vanbanden/chi_tiet_vb_den.html', {
        'vb': vb,
        'vb_truoc': vb_truoc,
        'vb_sau': vb_sau,
        'total_vb': total_vb
    })

def tao_du_thao(request):
    # Trả về template taoduthao.html
    return render(request, 'vanbandi/tao_du_thao.html')
from django.shortcuts import render, get_object_or_404, redirect
from .models import VanBanDen
from datetime import datetime
from .models import PhongBan

def sua_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)

    # Lấy list phòng ban để hiển thị select trong form
    phongbans = PhongBan.objects.all()

    if request.method == 'POST':
        # Gán đúng tên trường theo model của bạn
        vb.SoHieu = request.POST.get('SoHieu')  # trước: SoKyHieu
        vb.TrichYeu = request.POST.get('TrichYeu')
        vb.LoaiVBDen = request.POST.get('LoaiVBDen')  # trước: LoaiVanBan
        vb.DonViPhatHanh = request.POST.get('DonViPhatHanh')  # trước: CoQuanBanHanh

        # Xử lý ngày (form gửi 'YYYY-MM-DD')
        ngay_bh = request.POST.get('NgayBanHanh')
        ngay_den = request.POST.get('NgayDen')
        try:
            vb.NgayBanHanh = datetime.strptime(ngay_bh, '%Y-%m-%d')
        except (TypeError, ValueError):
            vb.NgayBanHanh = vb.NgayBanHanh  # giữ nguyên nếu không hợp lệ

        try:
            vb.NgayDen = datetime.strptime(ngay_den, '%Y-%m-%d')
        except (TypeError, ValueError):
            vb.NgayDen = vb.NgayDen

        # Độ khẩn / độ mật (nếu bạn dùng choices)
        vb.DoKhan = request.POST.get('DoKhan', vb.DoKhan)
        vb.DoMat = request.POST.get('DoMat', vb.DoMat)

        # Phòng ban — ở form ta sẽ gửi MaPhongBan (id)
        phongban_id = request.POST.get('MaPhongBan')
        if phongban_id:
            try:
                vb.MaPhongBan = PhongBan.objects.get(id=int(phongban_id))
            except (PhongBan.DoesNotExist, ValueError):
                # nếu id không đúng, giữ nguyên hoặc đặt None tùy model
                pass

        # Nội dung
        vb.NoiDung = request.POST.get('NoiDung', vb.NoiDung)

        vb.save()
        return redirect('chi_tiet_vb_den', vb_id=vb.id)

    # GET: render form, truyền vb và danh sách phòng ban
    return render(request, 'vanbanden/sua_van_ban_den.html', {
        'vb': vb,
        'phongbans': phongbans,
    })


