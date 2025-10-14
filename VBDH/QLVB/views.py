from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import VanBanDen, VanBanDi
from django.db.models import Q
from .models import VanBanDen, VanBanDi, PhongBan



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



