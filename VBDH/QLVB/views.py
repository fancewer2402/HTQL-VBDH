from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import VanBanDi, VanBanDen


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

def them_van_ban(request):
    return render(request, 'vanbanden/create.html')

def ds_vanbandi(request):
    ds = VanBanDi.objects.all().order_by('-NgayBanHanh')
    return render(request, 'vanbandi/vanbandi.html', {'ds_vanbandi': ds})

def vanbandi_detail(request, pk):
    vb = get_object_or_404(VanBanDi, pk=pk)
    return render(request, 'vanbandi/vanbandi_detail.html', {'vb': vb})


def tao_du_thao(request):
    # Trả về template taoduthao.html
    return render(request, 'vanbandi/tao_du_thao.html')
