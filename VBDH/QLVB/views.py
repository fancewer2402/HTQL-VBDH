from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from datetime import timedelta, date
from .models import VanBanDi, VanBanDen, ThongBao, NhatKyCongViec, PhongBan, PhanCongCongViec
from accounts.models import User as NhanVien
import os
from django.db import transaction
from .forms import VanBanDiForm, VanBanDiEditForm
from django.contrib.auth.decorators import login_required
import logging
logger = logging.getLogger(__name__)


# === DASHBOARD PLACEHOLDERS (CẦN THÊM VÀO urls.py) ===
def dashboard_quanly(request):
    # Logic của bạn ở đây.
    # Đảm bảo bạn đang render hoặc redirect đến một template/URL hợp lệ.
    from django.shortcuts import redirect
    return redirect('vanbandi') # Ví dụ về cách 1: Chuyển hướng


def dashboard_vanthu(request):
    return render(request, 'QLVB/dashboard_vanthu.html', {'title': 'Văn thư Dashboard'})


def dashboard_nhanvien(request):
    # Dùng vanbandi làm dashboard tạm thời cho Nhân viên nếu chưa có template
    return redirect('vanbandi')


# === XỬ LÝ ĐĂNG NHẬP / ĐĂNG XUẤT ===
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


def user_logout(request):
    logout(request)
    return redirect('login')


# === CHỨC NĂNG CHUNG ===
def get_current_nhanvien(request):
    try:
        return NhanVien.objects.filter(email=request.user.email).first()
    except Exception:
        return None


def global_notifications(request):
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())

    today_notifications = ThongBao.objects.filter(NgayTao__date=now.date())
    week_notifications = ThongBao.objects.filter(NgayTao__gte=start_of_week, NgayTao__lt=now.date())
    old_notifications = ThongBao.objects.filter(NgayTao__lt=start_of_week)
    notification_count = ThongBao.objects.count()

    return {
        'today_notifications': today_notifications,
        'week_notifications': week_notifications,
        'old_notifications': old_notifications,
        'notification_count': notification_count
    }


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
    context.update(global_notifications(request))
    return render(request, 'home.html', context)


def mark_notification_read(request, id):
    thongbao = get_object_or_404(ThongBao, id=id)
    thongbao.DaDoc = True
    thongbao.save()
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


def tra_cuu_van_ban(request):
    return render(request, 'QLVB/tra_cuu_van_ban.html')


def them_van_ban(request):
    return render(request, 'vanbanden/create.html')


# === VĂN BẢN ĐI (VANBANDI) ===
def ds_vanbandi(request):
    # CẬP NHẬT: Sắp xếp ưu tiên theo NgayTao giảm dần (-NgayTao) để văn bản mới tạo luôn nằm trên cùng.
    # NgayBanHanh (-NgayBanHanh) được sử dụng làm sắp xếp phụ.
    vanbandi_list = VanBanDi.objects.all().order_by('-NgayTao', '-NgayBanHanh')

    # Lọc theo từ khóa
    keyword = request.GET.get('keyword', '').strip()
    if keyword:
        vanbandi_list = vanbandi_list.filter(
            Q(SoHieu__icontains=keyword) |
            Q(TrichYeu__icontains=keyword)
        )

    # Lọc theo đơn vị nhận
    agency = request.GET.get('agency', '').strip()
    if agency:
        vanbandi_list = vanbandi_list.filter(DonViNhan__icontains=agency)

    # Lọc theo ngày tạo
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if from_date:
        try:
            from_date_parsed = parse_date(from_date)
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

    # Lọc theo phòng ban (qua MaNhanVien → MaPhongBan)
    department = request.GET.get('department')
    if department:
        vanbandi_list = vanbandi_list.filter(MaNhanVien__MaPhongBan_id=department)

    # Lọc theo loại văn bản
    doc_type = request.GET.get('doc_type')
    if doc_type:
        vanbandi_list = vanbandi_list.filter(LoaiVbDi=doc_type)

    # Phân trang
    paginator = Paginator(vanbandi_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Danh sách phòng ban để hiển thị trong select
    phongban_list = PhongBan.objects.all()

    context = {
        'ds_vanbandi': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'phongban_list': phongban_list,
        'keyword': keyword,
        'agency': agency,
        'from_date': from_date,
        'to_date': to_date,
        'department': department,
        'doc_type': doc_type,
    }

    context.update(global_notifications(request))
    return render(request, 'vanbandi/vanbandi.html', context)
@login_required
def vanbandi_detail(request, pk):
    van_ban = get_object_or_404(VanBanDi, pk=pk)
    is_editable = False
    is_manager_reviewable = False

    current_user = request.user
    creator_user = van_ban.MaNhanVien
    # ********************************************************
    # *** VỊ TRÍ CHÈN LOGIC KIỂM TRA QUYỀN TRUY CẬP TỔNG QUÁT ***
    # ********************************************************
    # Nếu người dùng hiện tại là Nhân viên ('NV')
    # VÀ không phải là người tạo văn bản (pk khác nhau)
    # VÀ văn bản chưa ở trạng thái "Đã ban hành"
    # THÌ: Chặn truy cập.
    if current_user.vai_tro == 'NV' and current_user.pk != creator_user.pk and van_ban.TrangThai != 'Đã ban hành':
        # Trả về lỗi 403 Forbidden hoặc chuyển hướng về trang danh sách
        return HttpResponseForbidden("Bạn không có quyền xem văn bản này khi nó chưa được ban hành.")
    # === KIỂM TRA ĐIỀU KIỆN SỬA (CHO NHÂN VIÊN) ===
    if current_user.is_authenticated and creator_user:
        if van_ban.TrangThai == 'Chờ thông qua' and creator_user.pk == current_user.pk:
            is_editable = True

    # === KIỂM TRA ĐIỀU KIỆN TRƯỞNG PHÒNG DUYỆT ===
    if current_user.is_authenticated:
        # Kiểm tra vai trò: Trưởng Phòng ('TP') HOẶC Quản Lý ('QL')
        is_manager_role = current_user.vai_tro in ['QL', 'TP']
        is_pending = van_ban.TrangThai == 'Chờ thông qua'

        if is_manager_role and is_pending:
            # Đảm bảo cả người duyệt và người tạo đều có phòng ban
            if current_user.ma_phong_ban and creator_user.ma_phong_ban:

                # So sánh ID của Phòng Ban
                if current_user.ma_phong_ban.pk == creator_user.ma_phong_ban.pk:
                    is_manager_reviewable = True

    # ********************************************************
    # *** ĐIỀU CHỈNH CHÍNH: KIỂM TRA VÀ CHUYỂN HƯỚNG NGAY ***
    # ********************************************************
    if is_manager_reviewable:
        # Nếu người dùng có quyền duyệt và văn bản chờ duyệt, CHUYỂN HƯỚNG SANG TRANG THÔNG QUA
        # Tên URL: 'thong_qua_van_ban', Tham số: vb_id
        return redirect('thong_qua_van_ban', vb_id=pk)
    # === DÀNH CHO GIÁM ĐỐC: chuyển sang XÉT DUYỆT ===
    if current_user.is_authenticated:
        if current_user.vai_tro == "GD" and van_ban.TrangThai == "Chờ xét duyệt":
            return redirect('xetduyetvanbandi', id=pk)
    # === 4) VĂN THƯ → CHUYỂN SANG TRANG BAN HÀNH ================
    # ============================================================
    if current_user.is_authenticated:
        if current_user.vai_tro == "VT" and van_ban.TrangThai == "Chờ ban hành":
            return redirect('ban_hanh_van_ban', id=van_ban.id)
    # === HIỂN THỊ TRANG CHI TIẾT (Nếu không chuyển hướng) ===
    context = {
        'vb': van_ban,
        'is_editable': is_editable,
        'is_manager_reviewable': is_manager_reviewable, # Giá trị này sẽ luôn là False khi render template (vì đã redirect nếu là True)
    }
    context.update(global_notifications(request))
    return render(request, 'vanbandi/vanbandi_detail.html', context)


def sua_vanbandi(request, pk):
    vb = get_object_or_404(VanBanDi, pk=pk)

    if request.method == "POST":
        form = VanBanDiEditForm(request.POST, request.FILES, instance=vb)
        if form.is_valid():
            vb = form.save()
            messages.success(request, "✅ Cập nhật văn bản đi thành công!")
            # Không redirect, chỉ render lại form mới (theo logic gốc)
            return redirect('vanbandi_detail', pk=vb.pk)

        else:
            messages.error(request, "Vui lòng kiểm tra lại các trường bị lỗi.")
    else:
        form = VanBanDiEditForm(instance=vb)

    return render(request, "vanbandi/sua_vanbandi.html", {"form": form, "vb": vb})


def tao_du_thao(request):
    form = VanBanDiForm()
    context = {
        'form': form,
        'title': 'Tạo Văn Bản Dự Thảo Mới',
    }
    context.update(global_notifications(request))
    return render(request, 'vanbandi/tao_du_thao.html', context)


def xetduyetvanbandi(request, id):
    vb = get_object_or_404(VanBanDi, id=id)
    if request.method == "POST":
        if 'duyet' in request.POST:
            vb.TrangThai = "Đã duyệt"
            vb.save()
            return redirect('phancong_vanthu', id=vb.id)
    return render(request, 'vanbandi/xetduyetvanbandi.html', {'vb': vb})


def phan_cong_van_thu(request, id):
    vb = get_object_or_404(VanBanDi, id=id)
    return render(request, 'vanbandi/phan_cong_van_thu.html', {'vb': vb})


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

                # Tạo số hiệu tự động nếu chưa có
                if not vb.SoHieu or vb.SoHieu.strip() == "":
                    count = VanBanDi.objects.count() + 1
                    vb.SoHieu = f"{count}/CV-PCDL/{today.year}"

                # Cập nhật dữ liệu
                vb.Email = email_nguoi_nhan
                vb.DoMat = request.POST.get("DoMat", vb.DoMat)
                vb.DoKhan = request.POST.get("DoKhan", vb.DoKhan)
                vb.NgayBanHanh = today
                vb.TrangThai = "Đã ban hành"
                vb.save()

                # Nội dung email
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
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email_nguoi_nhan],
                )
                email.attach_alternative(html_content, "text/html")

                # Đính kèm file nếu có
                if vb.FileDinhKem and hasattr(vb.FileDinhKem, 'path') and os.path.exists(vb.FileDinhKem.path):
                    email.attach_file(vb.FileDinhKem.path)

                try:
                    email.send()
                    messages.success(request, f"ĐÃ BAN HÀNH + GỬI EMAIL THÀNH CÔNG đến: <strong>{email_nguoi_nhan}</strong>")
                except Exception as e:
                    messages.warning(request, f"Đã ban hành nhưng <strong>gửi email thất bại</strong>: {str(e)}")
                    logger.exception("[EMAIL ERROR]")

                # Tạo thông báo nội bộ
                ThongBao.objects.create(
                    TieuDe=f"Văn bản '{vb.TrichYeu}' đã ban hành",
                    NoiDung=f"Số hiệu: {vb.SoHieu} | Gửi đến: {email_nguoi_nhan}",
                    MaNhanVien=vb.MaNhanVien,
                    MaVBDi=vb,
                )

                # Cập nhật phân công + nhật ký
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


def trang_thong_qua(request, vb_id):
    vb = get_object_or_404(VanBanDi, id=vb_id)
    danh_sach_quan_ly = NhanVien.objects.filter(vai_tro="QL")
    truong_phong = NhanVien.objects.filter(id=request.user.pk).first()

    if request.method == "POST":
        action = request.POST.get("action")
        ly_do = request.POST.get("ly_do_tu_choi", "")
        quan_ly_id = request.POST.get("quan_ly_chon")
        quan_ly = NhanVien.objects.filter(id=quan_ly_id).first() if quan_ly_id else None

        if action == "thongqua":
            if not quan_ly:
                messages.error(request, "⚠️ Phải chọn quản lý trước khi thông qua.")
                context = {"vb": vb, "danh_sach_quan_ly": danh_sach_quan_ly, "truong_phong": truong_phong}
                context.update(global_notifications(request))
                return render(request, "vanbandi/thongqua.html", context)

            file_chu_ky = request.FILES.get("file_chu_ky")
            if file_chu_ky:
                vb.FileChuKy = file_chu_ky

            vb.TrangThai = "Chờ phê duyệt"
            vb.save()

            ThongBao.objects.create(
                TieuDe="Yêu cầu phê duyệt văn bản đi",
                NoiDung=f"Trưởng phòng {truong_phong.HoTen if truong_phong else 'N/A'} trình duyệt văn bản đi '{vb.TrichYeu}'.",
                MaNhanVien=quan_ly,
                MaVBDi=vb
            )
            messages.success(request, f"Văn bản '{vb.TrichYeu}' đã được trình duyệt. Trạng thái: Chờ phê duyệt.")

        elif action == "tuchoi":
            vb.TrangThai = "Từ chối thông qua"
            vb.save()

            if vb.MaNhanVien:
                ThongBao.objects.create(
                    TieuDe="Dự thảo bị từ chối",
                    NoiDung=f"❌ Dự thảo '{vb.TrichYeu}' bị từ chối bởi Trưởng phòng {truong_phong.HoTen if truong_phong else 'N/A'}. Lý do: {ly_do or 'Không ghi rõ'}",
                    MaNhanVien=vb.MaNhanVien,
                    MaVBDi=vb
                )

            messages.warning(request, f"❌ Dự thảo '{vb.TrichYeu}' đã bị từ chối.")

        return redirect("vanbandi")

    context = {
        "vb": vb,
        "danh_sach_quan_ly": danh_sach_quan_ly,
        "truong_phong": truong_phong
    }
    context.update(global_notifications(request))
    return render(request, "vanbandi/thongqua.html", context)


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
    context.update(global_notifications(request))
    return render(request, 'QLVB/nhat_ky_hoat_dong.html', context)


# === VĂN BẢN ĐẾN (VANBANDEN) ===
def danh_sach_van_ban_den(request):
    van_ban_list = VanBanDen.objects.all().order_by('-NgayDen')

    # Lọc theo từ khóa
    keyword = request.GET.get('keyword', '').strip()
    if keyword:
        van_ban_list = van_ban_list.filter(
            Q(SoHieu__icontains=keyword) |
            Q(TrichYeu__icontains=keyword)
        )

    # Lọc theo đơn vị phát hành
    agency = request.GET.get('agency', '').strip()
    if agency:
        van_ban_list = van_ban_list.filter(DonViPhatHanh__icontains=agency)

    # Lọc theo ngày đến
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if from_date:
        try:
            from_date_parsed = parse_date(from_date)
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

    # Lọc theo phòng ban
    department = request.GET.get('department')
    if department:
        van_ban_list = van_ban_list.filter(MaPhongBan_id=department)

    # Lọc theo loại văn bản đến
    doc_type = request.GET.get('doc_type')
    if doc_type:
        van_ban_list = van_ban_list.filter(LoaiVBDen=doc_type)

    # Phân trang
    paginator = Paginator(van_ban_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Danh sách phòng ban
    phongban_list = PhongBan.objects.all()

    context = {
        'van_ban_list': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'phongban_list': phongban_list,
        'keyword': keyword,
        'agency': agency,
        'from_date': from_date,
        'to_date': to_date,
        'department': department,
        'doc_type': doc_type,
    }

    context.update(global_notifications(request))
    return render(request, 'vanbanden/danh_sach_van_ban_den.html', context)


def chi_tiet_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    vb_truoc = VanBanDen.objects.filter(id__lt=vb.id).order_by('-id').first()
    vb_sau = VanBanDen.objects.filter(id__gt=vb.id).order_by('id').first()
    total_vb = VanBanDen.objects.count()
    context = {
        'vb': vb,
        'vb_truoc': vb_truoc,
        'vb_sau': vb_sau,
        'total_vb': total_vb
    }
    context.update(global_notifications(request))
    return render(request, 'vanbanden/chi_tiet_vb_den.html', context)


def xet_duyet_vb_den(request, vb_id):
    vanbanden = get_object_or_404(VanBanDen, id=vb_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            vanbanden.TrangThai = "Chờ phân công"
            vanbanden.save()
            messages.success(request, f"Văn bản '{vanbanden.TrichYeu}' đã được duyệt. Chuyển sang Chờ phân công.")
            return redirect('phan_cong_nhan_vien_vbden', id=vanbanden.pk)
        elif action == 'reject':
            vanbanden.TrangThai = "Từ chối"
            vanbanden.save()
            messages.warning(request, f"Văn bản '{vanbanden.TrichYeu}' đã bị Từ chối.")
            return redirect('danh_sach_van_ban_den')

    context = {'vb': vanbanden}
    context.update(global_notifications(request))
    return render(request, 'vanbanden/xetduyet_vanbanden.html', context)


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

            PhanCongCongViec.objects.create(
                VanBanDen=vb,
                NguoiPhanCong=request.user,
                NguoiXuLy=nhanvien,
                TieuDe=tieude,
                MoTa=mota,
                HanChot=han_chot,
                TrangThai=PhanCongCongViec.TrangThai.CHO_XAC_NHAN,
            )

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
            messages.success(request, f"Đã phân công cho {nhanvien.HoTen if hasattr(nhanvien, 'HoTen') else nhanvien.username}.")
            return redirect("danh_sach_van_ban_den")

    context = {"vb": vb, "nhanviens": nhanviens}
    context.update(global_notifications(request))
    return render(request, "vanbanden/phancong_vanbanden.html", context)


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

    context = {"vb": vb, "nhanvien": nhanvien}
    context.update(global_notifications(request))
    return render(request, "vanbanden/xacnhan_phancong_vbden.html", context)


def bao_cao_vbden(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    if request.method == "POST":
        vb.TrangThai = "Hoàn thành"
        vb.save()
        messages.success(request, f"Văn bản '{vb.TrichYeu}' đã hoàn thành.")
        return redirect('danh_sach_van_ban_den')

    context = {"vb": vb}
    context.update(global_notifications(request))
    return render(request, "vanbanden/baocao_vbden.html", context)


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

        from datetime import datetime
        if ngay_bh:
            try:
                vb.NgayBanHanh = datetime.strptime(ngay_bh, '%Y-%m-%d')
            except:
                pass
        if ngay_den:
            try:
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
        messages.success(request, "Cập nhật văn bản đến thành công.")
        return redirect('chi_tiet_vb_den', vb_id=vb.id)

    context = {
        'vb': vb,
        'phongbans': phongbans,
    }
    context.update(global_notifications(request))
    return render(request, 'vanbanden/sua_van_ban_den.html', context)
