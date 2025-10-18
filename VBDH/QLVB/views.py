from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import VanBanDen, VanBanDi



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

def logout_confirm(request):
    if request.method == "POST":
        logout(request)
        return redirect('logout_success')
    return render(request, 'QLVB/logout_confirm.html')
def logout_success(request):
    return render(request, 'QLVB/logout_success.html')
def tra_cuu_van_ban(request):
    return render(request, 'QLVB/tra_cuu_van_ban.html')


from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import VanBanDen, PhongBan, NhanVien
from django.utils.dateparse import parse_date

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

    return render(request, 'QLVB/danh_sach_van_ban_den.html', {
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
    return render(request, 'QLVB/chi_tiet_vb_den.html', {
        'vb': vb,
        'vb_truoc': vb_truoc,
        'vb_sau': vb_sau
    })
