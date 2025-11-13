from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import VanBanDi, VanBanDen, ThongBao, NhatKyCongViec, PhongBan
from datetime import timedelta, date
from django.utils import timezone
from accounts.models import User as NhanVien






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


def sua_vanbandi(request, id):
   vb = get_object_or_404(VanBanDi, id=id)


   if request.method == 'POST':
       vb.TrichYeu = request.POST.get('TrichYeu')
       vb.SoKyHieu = request.POST.get('SoKyHieu')
       vb.NoiDung = request.POST.get('NoiDung')
       vb.save()
       return redirect('vanbandi_detail', pk=vb.id)  # ✅ Sửa đúng name


   return render(request, 'vanbandi/sua_vanbandi.html', {'vb': vb})


def get_current_nhanvien(request):
   # Nếu bạn chưa map user -> NhanVien, trả về None (đổi logic nếu cần)
   try:
       email = request.user.email
       return NhanVien.objects.filter(email=email).first()
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


# Xét duyệt văn bản đi
def xetduyetvanbandi(request, id):
   vb = get_object_or_404(VanBanDi, id=id)


   if request.method == "POST":
       # Giả sử có nút 'duyet' trong form
       if 'duyet' in request.POST:
           vb.trang_thai = "Đã duyệt"
           vb.save()
           # ✅ Sau khi duyệt, điều hướng sang trang phân công văn thư
           return redirect('phancong_vanthu', id=vb.id)


   return render(request, 'vanbandi/xetduyetvanbandi.html', {'vb': vb})




# Phân công văn thư
def phan_cong_van_thu(request, id):
   vb = get_object_or_404(VanBanDi, id=id)
   return render(request, 'vanbandi/phan_cong_van_thu.html', {'vb': vb})




def nhat_ky_hoat_dong(request, loaivanban, vanban_id):
   # Xác định loại văn bản
   if loaivanban == 'vanbanden':
       vanban = get_object_or_404(VanBanDen, id=vanban_id)
       nhatky = NhatKyCongViec.objects.filter(MaVBDen=vanban).order_by('NgayTao')
   elif loaivanban == 'vanbandi':
       vanban = get_object_or_404(VanBanDi, id=vanban_id)
       nhatky = NhatKyCongViec.objects.filter(MaVBDi=vanban).order_by('NgayTao')
   else:
       # Không hợp lệ
       nhatky = []
       vanban = None


   context = {
       'loaivanban': loaivanban,
       'vanban': vanban,
       'nhatky': nhatky,
   }
   return render(request, 'QLVB/nhat_ky_hoat_dong.html', context)


def ban_hanh_van_ban(request, id):
   vb = get_object_or_404(VanBanDi, id=id)
   today = timezone.now().date()   # Lấy ngày hiện tại (chỉ phần ngày, không có giờ)


   context = {
       'vb': vb,
       'today': today
   }
   return render(request, 'vanbandi/ban_hanh_van_ban.html', context)




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


def phan_cong_nhan_vien_vbden(request, id):
   # Lấy văn bản đến theo id
   vb = get_object_or_404(VanBanDen, id=id)


   # Lấy danh sách nhân viên thuộc cùng phòng ban
   nhanviens = NhanVien.objects.filter(MaPhongBan=vb.MaPhongBan)


   if request.method == "POST":
       ma_nhanvien_id = request.POST.get("MaNhanVien")
       tieude = request.POST.get("TieuDe")
       mota = request.POST.get("MoTa")
       han_chot = request.POST.get("HanChot")
       thao_tac = request.POST.get("ThaoTac")


       # Kiểm tra dữ liệu đầu vào
       if not all([ma_nhanvien_id, tieude, mota, han_chot, thao_tac]):
           messages.error(request, "⚠️ Vui lòng nhập đầy đủ thông tin trước khi lưu.")
       else:
           nhanvien = get_object_or_404(NhanVien, id=ma_nhanvien_id)


           # Tạo nhật ký công việc
           NhatKyCongViec.objects.create(
               MaVBDen=vb,
               MaNhanVien=nhanvien,
               TieuDe=tieude,
               MoTa=mota,
               HanChot=han_chot,
               ThaoTac=thao_tac,
               TrangThai=NhatKyCongViec.TrangThai.ChoXacNhan,
           )


           # Cập nhật trạng thái văn bản
           vb.TrangThai = "Chờ xác nhận"
           vb.save()


           messages.success(request, f"✅ Đã phân công xử lý văn bản cho {nhanvien.HoTen}.")
           return redirect("danh_sach_van_ban_den")


   context = {
       "vb": vb,
       "nhanviens": nhanviens,
   }
   return render(request, "vanbanden/phancong_vanbanden.html", context)


def xac_nhan_phan_cong_vbden(request, vb_id):
   """
   Nhân viên được phân công xác nhận rằng đã nhận xử lý văn bản đến.
   """
   vb = get_object_or_404(VanBanDen, id=vb_id)


   # Giả định user đăng nhập là nhân viên
   nhanvien = getattr(request.user, "nhanvien", None)


   # Tìm nhật ký công việc tương ứng
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


def bao_cao_vbden(request, vb_id):
   """
   Đánh dấu văn bản đến là 'Hoàn thành'
   """
   vb = get_object_or_404(VanBanDen, id=vb_id)


   if request.method == "POST":
       vb.TrangThai = "Hoàn thành"
       vb.save()
       messages.success(request, f"✅ Văn bản '{vb.TrichYeu}' đã được đánh dấu là Hoàn thành.")
       return redirect('danh_sach_van_ban_den')


   return render(request, "vanbanden/baocao_vbden.html", {"vb": vb})


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


