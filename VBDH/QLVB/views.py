# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import timedelta, date
from .models import VanBanDi, VanBanDen, ThongBao, NhatKyCongViec, PhongBan, PhanCongCongViec
from accounts.models import User as NhanVien
from django.contrib.auth import get_user_model
User = get_user_model()
import os
from django.db import transaction
from datetime import datetime


def user_login(request):
   if request.method == 'POST':
       username = request.POST.get('username')
       password = request.POST.get('password')


       user = authenticate(request, username=username, password=password)
       if user is not None:
           login(request, user)
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
   # Lấy tất cả văn bản đi
   vanbandi_list = VanBanDi.objects.all().order_by('-NgayBanHanh')


   # === LỌC THEO TỪ KHÓA ===
   keyword = request.GET.get('keyword', '').strip()
   if keyword:
       vanbandi_list = vanbandi_list.filter(
           Q(SoHieu__icontains=keyword) |
           Q(TrichYeu__icontains=keyword)
       )


   # === LỌC THEO ĐƠN VỊ NHẬN (tạm dùng DonViNhan) ===
   agency = request.GET.get('agency', '').strip()
   if agency:
       vanbandi_list = vanbandi_list.filter(DonViNhan__icontains=agency)


   # === LỌC THEO NGÀY TẠO ===
   from_date = request.GET.get('from_date')
   to_date = request.GET.get('to_date')


   if from_date:
       try:
           from_date_parsed = parse_date(from_date)  # dd/mm/yyyy → yyyy-mm-dd
           if from_date_parsed:
               vanbandi_list = vanbandi_list.filter(NgayTao__date__gte=from_date_parsed)
       except:
           pass


   if to_date:
       try:
           to_date_parsed = parse_date(to_date)
           if to_date_parsed:
               vanbandi_list = vanbandi_list.filter(NgayTao__date__lte=to_date_parsed)
       except:
           pass


   # === LỌC THEO PHÒNG BAN (qua MaNhanVien → MaPhongBan) ===
   department = request.GET.get('department')
   if department:
       vanbandi_list = vanbandi_list.filter(MaNhanVien__MaPhongBan_id=department)


   # === LỌC THEO LOẠI VĂN BẢN ===
   doc_type = request.GET.get('doc_type')
   if doc_type:
       vanbandi_list = vanbandi_list.filter(LoaiVbDi=doc_type)


   # === PHÂN TRANG ===
   paginator = Paginator(vanbandi_list, 10)  # 10 văn bản/trang
   page_number = request.GET.get('page')
   page_obj = paginator.get_page(page_number)


   # === LẤY DANH SÁCH PHÒNG BAN ĐỂ HIỂN THỊ TRONG SELECT ===
   phongban_list = PhongBan.objects.all()


   context = {
       'ds_vanbandi': page_obj,
       'page_obj': page_obj,
       'paginator': paginator,
       'phongban_list': phongban_list,


       # Giữ lại giá trị đã chọn trên form
       'keyword': keyword,
       'agency': agency,
       'from_date': from_date,
       'to_date': to_date,
       'department': department,
       'doc_type': doc_type,
   }

   context.update(global_notifications(request))
   return render(request, 'vanbandi/vanbandi.html', context)




def vanbandi_detail(request, pk):
   vb = get_object_or_404(VanBanDi, pk=pk)
   return render(request, 'vanbandi/vanbandi_detail.html', {'vb': vb})

def sua_vanbandi(request, id):
   vb = get_object_or_404(VanBanDi, id=id)


   if request.method == 'POST':
       vb.TrichYeu = request.POST.get('TrichYeu')
       vb.SoHieu = request.POST.get('SoHieu', vb.SoHieu)  # Sửa: dùng SoHieu
       vb.NoiDung = request.POST.get('NoiDung')
       vb.save()
       return redirect('vanbandi_detail', pk=vb.id)


   return render(request, 'vanbandi/sua_vanbandi.html', {'vb': vb})

def get_current_nhanvien(request):
   try:
       return NhanVien.objects.filter(email=request.user.email).first()
   except Exception:
       return None

def danh_sach_van_ban_den(request):
   van_ban_list = VanBanDen.objects.all().order_by('-NgayDen')


   # === LỌC THEO TỪ KHÓA ===
   keyword = request.GET.get('keyword', '').strip()
   if keyword:
       van_ban_list = van_ban_list.filter(
           Q(SoHieu__icontains=keyword) |
           Q(TrichYeu__icontains=keyword)
       )


   # === LỌC THEO ĐƠN VỊ PHÁT HÀNH ===
   agency = request.GET.get('agency', '').strip()
   if agency:
       van_ban_list = van_ban_list.filter(DonViPhatHanh__icontains=agency)


   # === LỌC THEO NGÀY ĐẾN ===
   from_date = request.GET.get('from_date')
   to_date = request.GET.get('to_date')


   if from_date:
       try:
           from_date_parsed = parse_date(from_date)  # dd/mm/yyyy → yyyy-mm-dd
           if from_date_parsed:
               van_ban_list = van_ban_list.filter(NgayDen__date__gte=from_date_parsed)
       except:
           pass


   if to_date:
       try:
           to_date_parsed = parse_date(to_date)
           if to_date_parsed:
               van_ban_list = van_ban_list.filter(NgayDen__date__lte=to_date_parsed)
       except:
           pass


   # === LỌC THEO PHÒNG BAN ===
   department = request.GET.get('department')
   if department:
       van_ban_list = van_ban_list.filter(MaPhongBan_id=department)


   # === LỌC THEO LOẠI VĂN BẢN ĐẾN ===
   doc_type = request.GET.get('doc_type')
   if doc_type:
       van_ban_list = van_ban_list.filter(LoaiVBDen=doc_type)


   # === PHÂN TRANG ===
   paginator = Paginator(van_ban_list, 10)
   page_number = request.GET.get('page')
   page_obj = paginator.get_page(page_number)


   # === DANH SÁCH PHÒNG BAN ===
   phongban_list = PhongBan.objects.all()


   context = {
       'van_ban_list': page_obj,  # Dùng chung tên với template
       'page_obj': page_obj,
       'paginator': paginator,
       'phongban_list': phongban_list,


       # Giữ giá trị form
       'keyword': keyword,
       'agency': agency,
       'from_date': from_date,
       'to_date': to_date,
       'department': department,
       'doc_type': doc_type,
   }


   return render(request, 'vanbanden/danh_sach_van_ban_den.html', context)


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
    """Nhân viên tạo dự thảo và trình duyệt lên Trưởng phòng."""
        # ⚙️ Giả sử nhân viên đang đăng nhập
    nhanvien = User.objects.first()
    count = VanBanDi.objects.count() + 1
    so_hieu_tu_dong = f"VB-{datetime.now().year}-{count:04d}"

        # ✅ Tạo văn bản mới

    danh_sach_yeu_cau_list = VanBanDen.objects.filter(
        TrangThai='Đang xử lý',
        YeuCauVBDi=1  # chỉ lấy những văn bản có yêu cầu
    )
    if request.method == "POST":
        ma_phong_ban_id = request.POST.get('MaPhongBan')
        vb = VanBanDi.objects.create(
            SoHieu=so_hieu_tu_dong,
            TrichYeu=request.POST.get("TrichYeu"),
            NoiDung=request.POST.get("NoiDung"),
            LoaiVbDi=request.POST.get("LoaiVbDi"),
            DonViNhan=request.POST.get("DonViNhan"),
            FileDinhKem=request.FILES.get("FileDinhKem"),
            MaNhanVien=nhanvien,
            TrangThai="Chờ thông qua",  # trạng thái đầu tiên
            MaPhongBan_id=ma_phong_ban_id,
        )

        # ✅ Xác định Trưởng phòng của phòng ban nhân viên
        truong_phong = User.objects.filter(
            ma_phong_ban_id=ma_phong_ban_id,
            vai_tro="TP"
        ).first()

        # ✅ Gửi thông báo hệ thống (không phải email)
        if truong_phong:
            ThongBao.objects.create(
                TieuDe=f"Nhân viên {nhanvien.ho_ten} trình duyệt dự thảo '{vb.TrichYeu}'.",
                NoiDung=f"Nhân viên {nhanvien.ho_ten} đã trình duyệt dự thảo '{vb.TrichYeu}'.",
                MaNhanVien=truong_phong,  # người nhận thông báo là trưởng phòng
                MaVBDi=vb
            )

        messages.success(request, " Văn bản đã được trình duyệt cho Trưởng phòng.")
        return redirect("vanbandi")  # chuyển về trang danh sách

    # GET → hiển thị form
    phong_ban_list = PhongBan.objects.all()
    return render(request, "vanbandi/tao_du_thao.html", {
        "phong_ban_list": phong_ban_list,
        "so_hieu_tu_dong": so_hieu_tu_dong,
        "danh_sach_yeu_cau_list" : danh_sach_yeu_cau_list,
    })

# Xét duyệt văn bản đi
def xetduyetvanbandi(request, id):
    vb = get_object_or_404(VanBanDi, id=id)

    # Lấy trưởng phòng nếu có nhân viên tạo văn bản
    truong_phong = None
    if vb.MaNhanVien:
        truong_phong = User.objects.filter(ma_phong_ban_id=vb.MaNhanVien.ma_phong_ban_id, vai_tro="TP").first()
    # Danh sách văn thư
    vanthus = User.objects.filter(vai_tro="VT")
    quanly = User.objects.first()

    if request.method == "POST":
        action = request.POST.get("action")
        ly_do = request.POST.get("ly_do", "").strip()
        van_thu_id = request.POST.get("van_thu")
        han_cuoi = request.POST.get("han_cuoi")
        chu_ky = request.FILES.get("chu_ky")
        noi_dung_phan_cong = request.POST.get("noi_dung_phan_cong", "").strip()

        if action == "pheduyet":
            # Bắt buộc nhập khi phê duyệt
            if not (chu_ky and van_thu_id and han_cuoi):
                messages.error(request, "⚠️ Vui lòng nhập đầy đủ chữ ký, văn thư, hạn cuối trước khi phê duyệt!")
                return redirect('xetduyetvanbandi', id=vb.id)

            # Lưu dữ liệu phê duyệt
            vb.ChuKy = chu_ky
            vb.HanCuoi = han_cuoi
            vb.NoiDungPhanCong = noi_dung_phan_cong
            van_thu = NhanVien.objects.filter(id=van_thu_id, vai_tro="VT").first()
            vb.VanThuPhuTrach = van_thu
            vb.TrangThai = "Chờ ban hành"
            vb.save()

            # Thông báo đã duyệt cho người tạo văn bản + trưởng phòng
            msg_duyet = f" Văn bản '{vb.TrichYeu}' đã được quản lý {quanly.ho_ten} phê duyệt."
            if vb.MaNhanVien:
                ThongBao.objects.create(MaNhanVien=vb.MaNhanVien, TieuDe=msg_duyet,
                                        NoiDung=msg_duyet, MaVBDi=vb)
            if truong_phong:
                ThongBao.objects.create(MaNhanVien=truong_phong, TieuDe=msg_duyet,
                                        NoiDung=msg_duyet, MaVBDi=vb)

            # Thông báo phân công cho văn thư
            if van_thu:
                msg_phancong = (
                    f" Bạn đã được quản lý {quanly.ho_ten} phân công xử lý văn bản '{vb.TrichYeu}'. "
                    f"Hạn cuối: {han_cuoi}. "
                    f"Nội dung: {noi_dung_phan_cong}"
                    f"Chu Ky: {chu_ky}"
                )
                ThongBao.objects.create(MaNhanVien=van_thu,
                                        TieuDe=f" Bạn được phân công xử lý văn bản '{vb.TrichYeu}'. ",
                                        NoiDung=msg_phancong,
                                        MaVBDi=vb)

            messages.success(request, " Văn bản đã được phê duyệt và phân công thành công.")

        elif action == "tuchoi":
            # Từ chối thì không cần chữ ký, văn thư, hạn cuối
            vb.TrangThai = "Từ chối phê duyệt"
            vb.LyDoTuChoi = ly_do
            vb.save()

            msg_tuchoi = f" Văn bản '{vb.TrichYeu}' đã bị quản lý {quanly.ho_ten} từ chối."
            if vb.MaNhanVien:
                ThongBao.objects.create(MaNhanVien=vb.MaNhanVien,TieuDe=msg_tuchoi,
                                        NoiDung=f" Lý do: {ly_do or 'Không ghi rõ'}", MaVBDi=vb)
            if truong_phong:
                ThongBao.objects.create(MaNhanVien=truong_phong, TieuDe=msg_tuchoi,
                                        NoiDung=f" Lý do: {ly_do or 'Không ghi rõ'}",MaVBDi=vb)

            messages.warning(request, " Văn bản đã bị từ chối.")

        return redirect('vanbandi_detail', vb.id)  # quay về danh sách văn bản đi

    return render(request, "vanbandi/xetduyetvanbandi.html", {
        "vb": vb,
        "vanthus": vanthus,
    })

def nhat_ky_hoat_dong(request, loaivanban, vanban_id):
   if loaivanban == 'vanbanden':
       vanban = get_object_or_404(VanBanDen, id=vanban_id)
       nhatky = NhatKyCongViec.objects.filter(MaVBDen=vanban).order_by('ThoiGian')
   elif loaivanban == 'vanbandi':
       vanban = get_object_or_404(VanBanDi, id=vanban_id)
       nhatky = NhatKyCongViec.objects.filter(MaVBDi=vanban).order_by('ThoiGian')
   else:
       nhatky = []
       vanban = None


   context = {
       'loaivanban': loaivanban,
       'vanban': vanban,
       'nhatky': nhatky,
   }
   return render(request, 'QLVB/nhat_ky_hoat_dong.html', context)






from django.core.mail import EmailMultiAlternatives  # ← DÙNG CÁI NÀY ĐỂ GỬI HTML
from django.utils.html import strip_tags


@transaction.atomic
def ban_hanh_van_ban(request, id):
   vb = get_object_or_404(VanBanDi, id=id)
   today = timezone.now().date()


   if request.method == "POST":
       if "cancel" in request.POST:
           messages.info(request, "Đã hủy ban hành văn bản.")
           return redirect("vanbandi")


       if "banhanh" in request.POST:
           try:
               email_nguoi_nhan = request.POST.get("Email", "").strip()
               if not email_nguoi_nhan:
                   messages.error(request, "Vui lòng nhập email người nhận.")
                   return render(request, "vanbandi/ban_hanh_van_ban.html", {"vb": vb, "today": today})


               # === TẠO SỐ HIỆU TỰ ĐỘNG ===
               if not vb.SoHieu or vb.SoHieu.strip() == "":
                   count = VanBanDi.objects.count() + 1
                   vb.SoHieu = f"{count}/CV-PCDL/{today.year}"


               # === CẬP NHẬT DỮ LIỆU ===
               vb.Email = email_nguoi_nhan
               vb.DoMat = request.POST.get("DoMat", vb.DoMat)
               vb.DoKhan = request.POST.get("DoKhan", vb.DoKhan)
               vb.NgayBanHanh = today
               vb.TrangThai = "Đã ban hành"
               vb.save()


               # === NỘI DUNG EMAIL ===
               subject = f"[Văn bản đi] {vb.SoHieu} - {vb.TrichYeu}"


               html_content = f"""
               <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                   <div style="background: #2b579a; color: white; padding: 15px; text-align: center;">
                       <h2 style="margin: 0;">CÔNG TY ĐIỆN LỰC ĐẮK LẮK</h2>
                   </div>
                   <div style="padding: 20px;">
                       <h3 style="color: #2b579a;">Kính gửi Quý cơ quan,</h3>
                       <p><strong>Văn bản đã được ban hành:</strong></p>
                       <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                           <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Số hiệu:</strong></td><td style="padding: 8px;">{vb.SoHieu}</td></tr>
                           <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Trích yếu:</strong></td><td style="padding: 8px;">{vb.TrichYeu}</td></tr>
                           <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Ngày ban hành:</strong></td><td style="padding: 8px;">{today.strftime('%d/%m/%Y')}</td></tr>
                           <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Độ khẩn:</strong></td><td style="padding: 8px;">{vb.get_DoKhan_display()}</td></tr>
                           <tr><td style="padding: 8px;"><strong>Độ mật:</strong></td><td style="padding: 8px;">{vb.get_DoMat_display()}</td></tr>
                       </table>
                       <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #2b579a; margin: 15px 0;">
                           <strong>Nội dung:</strong><br>
                           {vb.NoiDung.replace(chr(10), '<br>')}
                       </div>
                       <p><em>Trân trọng,<br><strong>Hệ thống Quản lý Văn bản - PC Đắk Lắk</strong></em></p>
                   </div>
                   <div style="background: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; color: #666;">
                       Email tự động từ hệ thống QLVB - Vui lòng không trả lời.
                   </div>
               </div>
               """


               text_content = strip_tags(html_content)  # Phiên bản text


               # === GỬI EMAIL HTML + TEXT ===
               email = EmailMultiAlternatives(
                   subject=subject,
                   body=text_content,
                   from_email=settings.DEFAULT_FROM_EMAIL,  # Dùng settings
                   to=[email_nguoi_nhan],
               )
               email.attach_alternative(html_content, "text/html")


               # === ĐÍNH KÈM FILE (nếu có) ===
               if vb.FileDinhKem and os.path.exists(vb.FileDinhKem.path):
                   email.attach_file(vb.FileDinhKem.path)


               try:
                   email.send()
                   messages.success(request, f"ĐÃ BAN HÀNH + GỬI EMAIL THÀNH CÔNG đến: <strong>{email_nguoi_nhan}</strong>")
               except Exception as e:
                   messages.warning(request, f"Đã ban hành nhưng <strong>gửi email thất bại</strong>: {str(e)}")
                   print(f"[EMAIL ERROR] {e}")


               # === TẠO THÔNG BÁO NỘI BỘ ===
               ThongBao.objects.create(
                   TieuDe=f"Văn bản '{vb.TrichYeu}' đã ban hành",
                   NoiDung=f"Số hiệu: {vb.SoHieu} | Gửi đến: {email_nguoi_nhan}",
                   MaNhanVien=vb.MaNhanVien,
                   MaVBDi=vb,
               )


               # === CẬP NHẬT PHÂN CÔNG + NHẬT KÝ ===
               phancong = PhanCongCongViec.objects.filter(VanBanDi=vb).first()
               if phancong:
                   phancong.TrangThai = PhanCongCongViec.TrangThai.DA_BAN_HANH
                   phancong.save()
                   NhatKyCongViec.objects.create(
                       PhanCong=phancong,
                       ThaoTac=f"Ban hành văn bản đi số {vb.SoHieu}",
                       TrangThai=PhanCongCongViec.TrangThai.DA_BAN_HANH,
                       NguoiThucHien=vb.MaNhanVien
                   )


               return redirect("vanbandi")


           except Exception as e:
               messages.error(request, f"Lỗi hệ thống: {str(e)}")


   return render(request, "vanbandi/ban_hanh_van_ban.html", {"vb": vb, "today": today})


def home(request):
   now = timezone.now()
   start_of_week = now - timedelta(days=now.weekday())


   today_notifications = ThongBao.objects.filter(NgayTao__date=now.date())
   week_notifications = ThongBao.objects.filter(NgayTao__gte=start_of_week, NgayTao__lt=now.date())
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
   vb = get_object_or_404(VanBanDen, id=id)
   nhanviens = NhanVien.objects.filter(MaPhongBan=vb.MaPhongBan)


   if request.method == "POST":
       ma_nhanvien_id = request.POST.get("MaNhanVien")
       tieude = request.POST.get("TieuDe")
       mota = request.POST.get("MoTa")
       han_chot = request.POST.get("HanChot")
       thao_tac = request.POST.get("ThaoTac")


       if not all([ma_nhanvien_id, tieude, mota, han_chot, thao_tac]):
           messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
       else:
           nhanvien = get_object_or_404(NhanVien, id=ma_nhanvien_id)
           NhatKyCongViec.objects.create(
               MaVBDen=vb,
               MaNhanVien=nhanvien,
               TieuDe=tieude,
               MoTa=mota,
               HanChot=han_chot,
               ThaoTac=thao_tac,
               TrangThai=NhatKyCongViec.TrangThai.CHO_XAC_NHAN,
           )
           vb.TrangThai = "Chờ xác nhận"
           vb.save()
           messages.success(request, f"Đã phân công cho {nhanvien.HoTen}.")
           return redirect("danh_sach_van_ban_den")


   return render(request, "vanbanden/phancong_vanbanden.html", {"vb": vb, "nhanviens": nhanviens})



def xac_nhan_phan_cong_vbden(request, vb_id):
   vb = get_object_or_404(VanBanDen, id=vb_id)
   nhanvien = get_current_nhanvien(request)
   nhatky = NhatKyCongViec.objects.filter(MaVBDen=vb, MaNhanVien=nhanvien).last()


   if request.method == "POST" and request.POST.get("action") == "confirm":
       if nhatky:
           nhatky.TrangThai = NhatKyCongViec.TrangThai.DANG_XU_LY
           nhatky.save()
       vb.TrangThai = "Đang xử lý"
       vb.save()
       messages.success(request, "Đã xác nhận xử lý văn bản.")
       return redirect("bao_cao_vbden", vb_id=vb.id)


   return render(request, "vanbanden/xacnhan_phancong_vbden.html", {"vb": vb, "nhanvien": nhanvien})



def bao_cao_vbden(request, vb_id):
   vb = get_object_or_404(VanBanDen, id=vb_id)
   if request.method == "POST":
       vb.TrangThai = "Hoàn thành"
       vb.save()
       messages.success(request, f"Văn bản '{vb.TrichYeu}' đã hoàn thành.")
       return redirect('danh_sach_van_ban_den')
   return render(request, "vanbanden/baocao_vbden.html", {"vb": vb})




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
       if ngay_bh:
           try:
               from datetime import datetime
               vb.NgayBanHanh = datetime.strptime(ngay_bh, '%Y-%m-%d')
           except:
               pass
       if ngay_den:
           try:
               from datetime import datetime
               vb.NgayDen = datetime.strptime(ngay_den, '%Y-%m-%d')
           except:
               pass


       vb.DoKhan = request.POST.get('DoKhan', vb.DoKhan)
       vb.DoMat = request.POST.get('DoMat', vb.DoMat)
       vb.NoiDung = request.POST.get('NoiDung', vb.NoiDung)


       phongban_id = request.POST.get('MaPhongBan')
       if phongban_id:
           try:
               vb.MaPhongBan = PhongBan.objects.get(id=int(phongban_id))
           except:
               pass


       vb.save()
       return redirect('chi_tiet_vb_den', vb_id=vb.id)


   return render(request, 'vanbanden/sua_van_ban_den.html', {
       'vb': vb,
       'phongbans': phongbans,
   })

from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('login')

def trang_thong_qua(request, vb_id):
    vb = get_object_or_404(VanBanDi, id=vb_id)
    danh_sach_quan_ly = User.objects.filter(vai_tro="QL")  # Lấy tất cả quản lý
    truong_phong = User.objects.filter(vai_tro="TP").first()

    if request.method == "POST":
        action = request.POST.get("action")
        ly_do = request.POST.get("ly_do_tu_choi", "")
        quan_ly_id = request.POST.get("quan_ly_chon")
        quan_ly = User.objects.filter(id=quan_ly_id).first() if quan_ly_id else None

        if action == "thongqua":
            if not quan_ly:
                messages.error(request, "⚠️ Phải chọn quản lý trước khi thông qua.")
                return render(request, "vanbandi/thongqua.html", {"vb": vb, "danh_sach_quan_ly": danh_sach_quan_ly})
            file_chu_ky = request.FILES.get("file_chu_ky")
            if file_chu_ky:
                vb.FileChuKy = file_chu_ky

            vb.TrangThai = "Chờ phê duyệt"
            vb.save()

            # 🔔 Gửi thông báo cho quản lý đã chọn
            ThongBao.objects.create(
                TieuDe=f" Trưởng phòng {truong_phong.ho_ten} trình duyệt văn bản '{vb.TrichYeu}'.",
                NoiDung=f" Trưởng phòng {truong_phong.ho_ten} trình duyệt văn bản '{vb.TrichYeu}'.",
                MaNhanVien=quan_ly,
                MaVBDi=vb
            )

            messages.success(request, f" Văn bản '{vb.TrichYeu}' đã được trình duyệt.")

        elif action == "tuchoi":
            vb.TrangThai = "Từ chối thông qua"
            vb.save()

            if vb.MaNhanVien and truong_phong:
                ThongBao.objects.create(
                    TieuDe=f"Dự thảo '{vb.TrichYeu}' bị từ chối",
                    NoiDung=f" Dự thảo '{vb.TrichYeu}' bị từ chối bởi Trưởng phòng {truong_phong.ho_ten}. "
                            f"Lý do: {ly_do or 'Không ghi rõ'}",
                    MaNhanVien=vb.MaNhanVien,
                    MaVBDi=vb)

            messages.warning(request, f" Dự thảo '{vb.TrichYeu}' đã bị từ chối.")

        return redirect('vanbandi_detail', vb.id)
    return render(request, "vanbandi/thongqua.html", {"vb": vb, "danh_sach_quan_ly": danh_sach_quan_ly})