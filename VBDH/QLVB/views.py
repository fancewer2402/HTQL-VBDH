from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import timedelta, date
from .models import VanBanDi, VanBanDen, ThongBao, NhatKyCongViec, PhongBan, PhanCongCongViec, TrangThaiCongViec
from accounts.models import User as NhanVien
from django.contrib.auth import get_user_model
User = get_user_model()
import os
from django.db import transaction
from datetime import datetime
from .forms import VanBanDiEditForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth import authenticate, login
from .models import VanBanDi, VanBanDen, ThongBao, NhatKyCongViec, PhongBan, PhanCongCongViec, DOKHAN_CHOICES, DOMAT_CHOICES
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.decorators import permission_required

from django.db.models import Max
from django.contrib.auth.decorators import login_required

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('danh_sach_van_ban_den')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")

    return render(request, 'QLVB/login.html')

@login_required
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

def get_so_hieu_tu_dong():
    """Tạo Số hiệu tự động: VB/YYYY/NNN"""
    today = datetime.now()
    year = today.strftime("%Y")

    last_vb = VanBanDen.objects.filter(
        NgayTao__year=year
    ).aggregate(Max('SoHieu'))['SoHieu__max']

    if last_vb:
        try:
            last_number = int(last_vb.split('/')[-1])
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0

    new_number = last_number + 1
    return f"VB/{year}/{new_number:03d}"

@login_required
@permission_required('QLVB.tao_vanbanden', raise_exception=True)
@login_required
@permission_required('QLVB.tao_vanbanden', raise_exception=True)
def them_van_ban(request):
    context = {
        'phong_ban_list': PhongBan.objects.all(),
        'nhan_vien_list': User.objects.filter(vai_tro='QL').order_by('ho_ten'),
        'DOKHAN_CHOICES': DOKHAN_CHOICES,
        'DOMAT_CHOICES': DOMAT_CHOICES,
        'loai_vb_list': VanBanDen.objects.values_list(
            'LoaiVBDen', flat=True
        ).distinct().order_by('LoaiVBDen'),
        'so_hieu_tu_dong': get_so_hieu_tu_dong(),
        'initial_data': {}
    }

    # =========================
    # GET
    # =========================
    if request.method == 'GET':
        return render(request, "vanbanden/create.html", context)

    data = request.POST
    files = request.FILES
    context['initial_data'] = data
    don_vi_phat_hanh = data.get('DonViPhatHanh', '').strip()
    if not don_vi_phat_hanh:
        messages.error(request, "Vui lòng nhập đơn vị phát hành văn bản.")
        return render(request, "vanbanden/create.html", context)
    # =========================
    # VALIDATION
    # =========================

    # 1. Phòng ban
    phong_ban = None
    ma_phong_ban_id = data.get('MaPhongBan')
    if not ma_phong_ban_id:
        messages.error(request, "Vui lòng chọn Phòng ban.")
        return render(request, "vanbanden/create.html", context)

    phong_ban = PhongBan.objects.filter(pk=ma_phong_ban_id).first()
    if not phong_ban:
        messages.error(request, "Phòng ban không tồn tại.")
        return render(request, "vanbanden/create.html", context)

    # 2. Trích yếu
    trich_yeu = data.get('TrichYeu', '').strip()
    if len(trich_yeu) <= 5:
        messages.error(request, "Trích yếu phải lớn hơn 5 ký tự.")
        return render(request, "vanbanden/create.html", context)
    # loai van ban
    loai_vb = data.get('LoaiVBDen', '').strip()

    if not loai_vb:
        messages.error(request, "Vui lòng chọn loại văn bản.")
        return render(request, "vanbanden/create.html", context)
    # 3. Ngày
    try:
        ngay_ban_hanh = date.fromisoformat(data.get('NgayBanHanh'))
        ngay_den = date.fromisoformat(data.get('NgayDen'))
    except (TypeError, ValueError):
        messages.error(request, "Ngày ban hành hoặc ngày đến không hợp lệ.")
        return render(request, "vanbanden/create.html", context)

    if ngay_den < ngay_ban_hanh:
        messages.error(
            request,
            "Ngày đến phải lớn hơn hoặc bằng ngày ban hành."
        )
        return render(request, "vanbanden/create.html", context)

    if ngay_den > date.today():
        messages.error(
            request,
            "Ngày đến không được lớn hơn ngày hôm nay."
        )
        return render(request, "vanbanden/create.html", context)

    # 4. Người nhận trình ký
    nguoi_trinh_ky = None
    nguoi_trinh_ky_id = data.get('NguoiNhanTrinhKy')

    if not nguoi_trinh_ky_id:
        messages.error(
            request,
            "Vui lòng chọn người nhận trình ký."
        )
        return render(request, "vanbanden/create.html", context)

    nguoi_trinh_ky = User.objects.filter(
        id=nguoi_trinh_ky_id,
        vai_tro='QL'
    ).first()

    if not nguoi_trinh_ky:
        messages.error(
            request,
            "Người nhận trình ký không hợp lệ hoặc không phải Quản lý."
        )
        return render(request, "vanbanden/create.html", context)
    # =========================
    # CREATE
    # =========================
    try:
        vb = VanBanDen.objects.create(
            SoHieu=get_so_hieu_tu_dong(),
            TrichYeu=trich_yeu,
            LoaiVBDen=loai_vb,
            DonViPhatHanh=data.get('DonViPhatHanh'),
            NgayBanHanh=ngay_ban_hanh,
            NgayDen=ngay_den,
            NoiDung=data.get('NoiDung'),
            DoKhan=data.get('DoKhan', 'BINH THUONG'),
            DoMat=data.get('DoMat', 'BINH THUONG'),
            YeuCauVBDi=int(data.get('YeuCauVBDi', 0)),
            MaNhanVien=request.user,
            MaPhongBan=phong_ban,
            NguoiNhanTrinhKy=nguoi_trinh_ky,
            FileDinhKem=files.get('FileDinhKem')
        )
    except Exception:
        messages.error(
            request,
            "Có lỗi hệ thống xảy ra. Vui lòng thử lại."
        )

    NhatKyCongViec.objects.create(
        PhanCong=None,
        ThaoTac="Tạo văn bản đến",
        TrangThai=vb.TrangThai,
        NguoiThucHien=request.user,
        MaVBDen=vb
    )

    messages.success(request, "Thêm văn bản đến thành công.")
    return redirect("danh_sach_van_ban_den")

@login_required
@permission_required('QLVB.xemdanhsach_vanbandi', raise_exception=True)
def ds_vanbandi(request):
    user = request.user

    # --- 1. NHÂN VIÊN: chỉ xem văn bản mình tạo ---
    if user.vai_tro == 'NV':
        vanbandi_list = VanBanDi.objects.filter(
            MaNhanVien=user
        ).order_by('-NgayTao', '-NgayBanHanh')
    else:
        # Các vai trò khác → xem tất cả (hoặc bạn có thể bổ sung quy định tùy ý)
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
    from_date = request.GET.get('from_date') or ''
    to_date = request.GET.get('to_date') or ''
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
    department = request.GET.get("department")
    if department:
        vanbandi_list = vanbandi_list.filter(
            MaNhanVien__ma_phong_ban__id=department
        )

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
@permission_required('QLVB.xemchitiet_vanbandi', raise_exception=True)
def vanbandi_detail(request, pk):
    van_ban = get_object_or_404(VanBanDi, pk=pk)
    user = request.user

    if not user.is_authenticated:
        return HttpResponseForbidden("Bạn không có quyền truy cập.")

    vai_tro = (getattr(user, "vai_tro", "") or "").strip().upper()
    trang_thai = (van_ban.TrangThai or "").strip()

    phancong = PhanCongCongViec.objects.filter(
        VanBanDi=van_ban,
        NguoiNhan=user
    ).first()

    if trang_thai == "Chờ thông qua":
        if vai_tro == "TP" and phancong:
                return redirect("thong_qua_van_ban", vb_id=van_ban.id)

    elif trang_thai == "Chờ phê duyệt":
        if vai_tro == "QL" and phancong:
            return redirect("xetduyetvanbandi", id=van_ban.id)

    elif trang_thai == "Chờ ban hành":
        if vai_tro == "VT" and phancong:
            return redirect("ban_hanh_van_ban", id=van_ban.id)

    is_editable = False
    if (
        user.id == getattr(van_ban.MaNhanVien, "id", None)
        and trang_thai == "Chờ thông qua"
    ):
        is_editable = True

    context = {
        "vb": van_ban,
        "is_editable": is_editable,
    }
    context.update(global_notifications(request))

    return render(request, "vanbandi/vanbandi_detail.html", context)

@login_required
@permission_required('QLVB.sua_vanbandi', raise_exception=True)
def sua_vanbandi(request, id):
    vb = get_object_or_404(VanBanDi, id=id)
    nhanvien = request.user

    if request.method == "POST":
        form = VanBanDiEditForm(request.POST, request.FILES, instance=vb)
        if form.is_valid():
            vb = form.save()
            messages.success(request, "Cập nhật văn bản đi thành công!")
            # Không redirect, chỉ render lại form mới (theo logic gốc)
            return redirect('vanbandi_detail', pk=vb.pk)
        else:
            messages.error(request, "Vui lòng kiểm tra lại các trường bị lỗi.")
    else:
        form = VanBanDiEditForm(instance=vb)

    NhatKyCongViec.objects.create(
        PhanCong=None,  # hoặc đối tượng PhanCongCongViec nếu có
        ThaoTac="Sửa văn bản đi",
        TrangThai=vb.TrangThai,
        NguoiThucHien=nhanvien,
        MaVBDi=vb
    )

    return render(request, "vanbandi/sua_vanbandi.html", {"form": form, "vb": vb})


from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)
@login_required
@permission_required('QLVB.xemchitiet_vanbanden', raise_exception=True)
def chi_tiet_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    user = request.user

    # Nếu user chưa đăng nhập → không có quyền gì
    if not user.is_authenticated:
        return HttpResponseForbidden("Bạn không có quyền truy cập.")

    # Lấy role và trạng thái rồi normalize (loại bỏ khoảng trắng, chuyển về uppercase)
    vai_tro = (getattr(user, "vai_tro", "") or "").strip().upper()
    # Nếu TrangThai là field choice, tốt hơn dùng get_TrangThai_display()
    trang_thai_raw = getattr(vb, "TrangThai", "") or ""
    trang_thai = trang_thai_raw.strip()

    # Có thể so sánh display value nếu bạn đã lưu choice key khác:
    try:
        trang_thai_display = vb.get_TrangThai_display()
    except Exception:
        trang_thai_display = trang_thai_raw

    if trang_thai == "Chờ xét duyệt" or trang_thai_display == "Chờ xét duyệt":
        if vai_tro == "VT":
            pass
        if vai_tro == "QL":
            return redirect("xet_duyet_vb_den", vb_id=vb.id)

    elif trang_thai == "Chờ xác nhận" or trang_thai_display == "Chờ xác nhận":
        if vai_tro == "NV":
            return redirect("xac_nhan_phan_cong_vbden", vb_id=vb.id)

    elif trang_thai == "Đang xử lý" or trang_thai_display == "Đang xử lý":
        if vai_tro == "NV":
            return redirect("bao_cao_vbden", vb_id=vb.id)

    is_editable = False
    # So sánh user instance bằng id để an toàn
    if getattr(user, "id", None) == getattr(vb.MaNhanVien, "id", None) and (trang_thai != "Hoàn thành" and trang_thai_display != "Hoàn thành"):
        is_editable = True

    context = {
        "vb": vb,
        "is_editable": is_editable,
    }

    return render(request, "vanbanden/chi_tiet_vb_den.html", context)


@login_required
@permission_required('QLVB.tao_vanbandi', raise_exception=True)
def tao_du_thao(request):
    nhanvien = request.user
    count = VanBanDi.objects.count() + 1
    so_hieu_tu_dong = f"VB-{datetime.now().year}-{count:04d}"

    danh_sach_yeu_cau_list = VanBanDen.objects.filter(
        TrangThai='Đang xử lý',
        YeuCauVBDi=1
    ).filter(
        Q(vanbandi__isnull=True) |
        Q(vanbandi__TrangThai='Chờ thông qua')
    ).distinct()

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
            TrangThai="Chờ thông qua",
            MaPhongBan_id=ma_phong_ban_id,
            MaVBDen_id=request.POST.get("MaVanBanDen"),
        )

        truong_phong = User.objects.filter(
            ma_phong_ban_id=ma_phong_ban_id,
            vai_tro="TP"
        ).first()

        if not truong_phong:
            messages.error(request, "Không tìm thấy Trưởng phòng.")
            return redirect("vanbandi")

        phancong = PhanCongCongViec.objects.create(
            TieuDe=f"Thông qua văn bản đi {vb.SoHieu}",
            MoTa=f"Nhân viên {nhanvien.ho_ten} trình dự thảo văn bản.",
            NguoiGiao=nhanvien,
            NguoiNhan=truong_phong,
            VanBanDi=vb,
            HanChot=timezone.now() + timezone.timedelta(days=2),
            TrangThai=TrangThaiCongViec.CHO_THONG_QUA
        )

        ThongBao.objects.create(
            TieuDe="Văn bản đi chờ thông qua",
            NoiDung=f"Dự thảo '{vb.TrichYeu}' cần được thông qua.",
            MaNhanVien=truong_phong,
            MaVBDi=vb
        )

        NhatKyCongViec.objects.create(
            PhanCong=phancong,
            ThaoTac="Tạo dự thảo văn bản đi",
            TrangThai=vb.TrangThai,
            NguoiThucHien=nhanvien,
            MaVBDi=vb
        )

        messages.success(request, "Văn bản đã được trình duyệt cho Trưởng phòng.")
        return redirect("vanbandi")
    phong_ban_list = PhongBan.objects.all()
    return render(request, "vanbandi/tao_du_thao.html", {
        "phong_ban_list": phong_ban_list,
        "so_hieu_tu_dong": so_hieu_tu_dong,
        "danh_sach_yeu_cau_list": danh_sach_yeu_cau_list,
    })

# Xét duyệt văn bản đi
@login_required
@permission_required('QLVB.xetduyet_vanbandi', raise_exception=True)
def xetduyetvanbandi(request, id):
    vb = get_object_or_404(VanBanDi, id=id)

    # Lấy trưởng phòng nếu có nhân viên tạo văn bản
    truong_phong = None
    if vb.MaNhanVien:
        truong_phong = User.objects.filter(ma_phong_ban_id=vb.MaNhanVien.ma_phong_ban_id, vai_tro="TP").first()
    # Danh sách văn thư
    vanthus = User.objects.filter(vai_tro="VT")
    quanly = request.user

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

            # Tạo bản phân công cho văn thư
            phan_cong = PhanCongCongViec.objects.create(
                TieuDe=f"Phân công ban hành: {vb.SoHieu}",
                MoTa=noi_dung_phan_cong,
                NguoiGiao=quanly,
                NguoiNhan=van_thu,
                VanBanDi=vb,
                HanChot=han_cuoi
            )

            # Lưu nhật ký hoạt động
            NhatKyCongViec.objects.create(
                PhanCong=phan_cong,
                ThaoTac="Xét duyệt",
                TrangThai=vb.TrangThai,
                NguoiThucHien=quanly,
                MaVBDi=vb
            )

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
            vb.TrangThai = "Bị từ chối"
            vb.LyDoTuChoi = ly_do
            vb.save()

            NhatKyCongViec.objects.create(
                PhanCong=None,
                ThaoTac="Xét duyệt",
                TrangThai=vb.TrangThai,
                NguoiThucHien=quanly
            )

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

@login_required
@permission_required('QLVB.xem_nhatky_vanbanden', raise_exception=True)
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
@login_required
@permission_required('QLVB.banhanh_vanbandi', raise_exception=True)
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
                   phancong.TrangThai = TrangThaiCongViec.DA_BAN_HANH
                   phancong.save()
                   NhatKyCongViec.objects.create(
                       PhanCong=phancong,
                       ThaoTac=f"Ban hành văn bản đi số {vb.SoHieu}",
                       TrangThai=vb.TrangThai,
                       NguoiThucHien=vb.MaNhanVien,
                       MaVBDi=vb
                   )
               return redirect("vanbandi")

           except Exception as e:
               messages.error(request, f"Lỗi hệ thống: {str(e)}")

   return render(request, "vanbandi/ban_hanh_van_ban.html", {"vb": vb, "today": today})

@login_required
@permission_required('QLVB.xemdanhsach_vanbanden', raise_exception=True)
def danh_sach_van_ban_den(request):
    user = request.user

    # --- an toàn cho AnonymousUser ---
    role = getattr(user, "vai_tro", None)

    # --- 1. Lọc theo vai trò ---
    if not user.is_authenticated:
        # Nếu chưa login → không cho xem danh sách
        return redirect("login")  # hoặc trang bạn muốn

    if role == "VT":  # Văn thư chỉ xem văn bản mình tạo
        van_ban_list = VanBanDen.objects.filter(MaNhanVien=user).order_by("-NgayTao")

    elif role == "NV":  # Nhân viên xem văn bản được phân công
        van_ban_list = (
            VanBanDen.objects
            .filter(phancongcongviec__NguoiNhan=user)
            .distinct()
            .order_by("-NgayTao")
        )

    else:  # QL, TP xem tất cả
        van_ban_list = VanBanDen.objects.all().order_by("-NgayTao")

    # --- Lọc theo từ khóa ---
    keyword = request.GET.get('keyword', '').strip()
    if keyword:
        van_ban_list = van_ban_list.filter(
            Q(SoHieu__icontains=keyword) |
            Q(TrichYeu__icontains=keyword)
        )

    # --- Lọc đơn vị phát hành ---
    agency = request.GET.get('agency', '').strip()
    if agency:
        van_ban_list = van_ban_list.filter(DonViPhatHanh__icontains=agency)

    # --- Lọc ngày ---
    from_date = request.GET.get('from_date') or ''
    to_date = request.GET.get('to_date') or ''

    if from_date:
        parse_from = parse_date(from_date)
        if parse_from:
            van_ban_list = van_ban_list.filter(NgayDen__date__gte=parse_from)

    if to_date:
        parse_to = parse_date(to_date)
        if parse_to:
            van_ban_list = van_ban_list.filter(NgayDen__date__lte=parse_to)

    # --- Lọc phòng ban ---
    department = request.GET.get('department')
    if department:
        van_ban_list = van_ban_list.filter(MaPhongBan_id=department)

    # --- Lọc loại văn bản ---
    doc_type = request.GET.get('doc_type')
    if doc_type:
        van_ban_list = van_ban_list.filter(LoaiVBDen=doc_type)

    # --- Phân trang ---
    paginator = Paginator(van_ban_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import (
    VanBanDen,
    PhanCongCongViec,
    NhatKyCongViec,
    ThongBao
)

@login_required
@permission_required('QLVB.xetduyet_vanbanden', raise_exception=True)
def xet_duyet_va_phan_cong_vbden(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "reject":
            ly_do = request.POST.get("ly_do_tu_choi", "").strip()

            vb.TrangThai = "Từ chối"
            vb.save()

            # Nhật ký
            NhatKyCongViec.objects.create(
                PhanCong=None,
                ThaoTac=f"Từ chối văn bản. Lý do: {ly_do}",
                TrangThai="Bị từ chối",
                NguoiThucHien=request.user,
                MaVBDen = vb
            )

            messages.warning(request, "Văn bản đã bị từ chối.")
            return redirect("danh_sach_van_ban_den")

        elif action == "approve":
            chu_ky = request.FILES.get("chu_ky")
            nguoi_xu_ly_id = request.POST.get("nguoi_xu_ly")
            han_xu_ly = request.POST.get("han_xu_ly")
            noi_dung = request.POST.get("noi_dung_phan_cong")

            if not all([nguoi_xu_ly_id, han_xu_ly, noi_dung, chu_ky]):
                messages.error(request, "Vui lòng nhập đầy đủ thông tin yêu cầu.")
                return redirect(request.path)

            nguoi_xu_ly = get_object_or_404(
                request.user.__class__, id=nguoi_xu_ly_id
            )

            phan_cong_ton_tai = PhanCongCongViec.objects.filter(
                VanBanDen=vb
            ).exclude(TrangThai="Bị từ chối").exists()

            if phan_cong_ton_tai:
                messages.warning(
                    request,
                    "Văn bản này đã được phân công trước đó."
                )
                return redirect("danh_sach_van_ban_den")

            # Cập nhật trạng thái văn bản
            vb.TrangThai = "Chờ xác nhận"
            vb.save()

            # Tạo phân công
            phan_cong = PhanCongCongViec.objects.create(
                TieuDe=f"Xử lý văn bản: {vb.TrichYeu}",
                MoTa=noi_dung,
                HanChot=han_xu_ly,
                NguoiGiao=request.user,
                NguoiNhan=nguoi_xu_ly,
                VanBanDen=vb,
                TrangThai="Chờ xác nhận"
            )

            # Nhật ký hệ thống
            NhatKyCongViec.objects.create(
                PhanCong=phan_cong,
                ThaoTac="Xét duyệt và phân công xử lý văn bản đến",
                TrangThai="Chờ xác nhận",
                NguoiThucHien=request.user
            )

            # Thông báo cho người được phân công
            ThongBao.objects.create(
                TieuDe=f"Bạn có văn bản đến số {vb.SoHieu} cần xử lý",
                NoiDung=f"Trích yếu: {vb.TrichYeu}",
                MaNhanVien=nguoi_xu_ly,
                MaVBDen=vb
            )

            messages.success(
                request,
                f"Đã xét duyệt và phân công cho {nguoi_xu_ly.get_full_name() or nguoi_xu_ly.username}."
            )
            return redirect("danh_sach_van_ban_den")

    context = {
        "vb": vb,
        "danh_sach_nguoi_dung": vb.MaPhongBan.nhan_viens.all()
    }
    return render(
        request,
        "vanbanden/xetduyet_vanbanden.html",
        context
    )

@login_required
@permission_required('QLVB.capnhat_trangthai_cv_vbden', raise_exception=True)
def xac_nhan_phan_cong_vbden(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    nhanvien = request.user

    # LẤY ĐÚNG PHÂN CÔNG CỦA NHÂN VIÊN ĐANG ĐĂNG NHẬP
    phan_cong = PhanCongCongViec.objects.filter(
        VanBanDen=vb,
        NguoiNhan=nhanvien
    ).order_by("-NgayTao").first()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "confirm":
            if not phan_cong:
                messages.error(request, "Không tìm thấy phân công hợp lệ.")
                return redirect(request.path)

            if phan_cong.TrangThai != "Chờ xác nhận":
                messages.warning(
                    request,
                    "Phân công này đã được xác nhận trước đó."
                )
                return redirect("bao_cao_vbden", vb_id=vb.id)

            # Cập nhật phân công
            phan_cong.TrangThai = "Đang xử lý"
            phan_cong.save()

            # Cập nhật văn bản
            vb.TrangThai = "Đang xử lý"
            vb.save()

            # Nhật ký
            NhatKyCongViec.objects.create(
                PhanCong=phan_cong,
                ThaoTac="Nhân viên xác nhận xử lý văn bản",
                TrangThai="Đang xử lý",
                NguoiThucHien=nhanvien,
                MaVBDen = vb.id
            )

            # Thông báo cho NGƯỜI GIAO
            ThongBao.objects.create(
                TieuDe=f"Văn bản {vb.SoHieu} đã được xác nhận xử lý",
                NoiDung=f"Nhân viên {nhanvien.get_full_name() or nhanvien.username} đã xác nhận.",
                MaNhanVien=phan_cong.NguoiGiao,
                MaVBDen=vb
            )

            messages.success(
                request,
                f"Đã xác nhận xử lý văn bản đến số {vb.SoHieu}."
            )
            return redirect("bao_cao_vbden", vb_id=vb.id)

    context = {
        "vb": vb,
        "nhanvien": nhanvien,
        "phan_cong": phan_cong,
    }

    return render(
        request,
        "vanbanden/xacnhan_phancong_vbden.html",
        context
    )

@login_required
@permission_required('QLVB.capnhat_trangthai_cv_vbden', raise_exception=True)
def bao_cao_vbden(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    nhanvien = request.user

    # LẤY VĂN BẢN ĐI GẮN VỚI VĂN BẢN ĐẾN (nếu có)
    vb_di = VanBanDi.objects.filter(MaVBDen=vb).first()

    # LẤY PHÂN CÔNG GẮN VỚI VB NÀY VÀ NGƯỜI ĐĂNG NHẬP (nếu có)
    phan_cong = PhanCongCongViec.objects.filter(
        VanBanDen=vb,
        NguoiNhan=nhanvien
    ).order_by("-NgayTao").first()

    if request.method == "POST":
        action = request.POST.get("action")

        if not phan_cong:
            messages.error(request, "Không tìm thấy phân công hợp lệ để báo cáo.")
            return redirect(request.path)

        if phan_cong.TrangThai != "Đang xử lý":
            messages.warning(request, "Công việc này đã được báo cáo hoặc không ở trạng thái đang xử lý.")
            return redirect("bao_cao_vbden", vb_id=vb.id)

        if vb.YeuCauVBDi == 1:
            if not vb_di:
                messages.error(request, "Văn bản này yêu cầu Văn bản đi nhưng chưa có văn bản đi liên kết.")
                return redirect(request.path)
            # kiểm tra trạng thái / số hiệu VB đi (tùy quy ước bạn dùng 'Đã ban hành' hoặc check SoHieu)
            if not getattr(vb_di, "SoHieu", None) or vb_di.TrangThai != "Đã ban hành":
                messages.warning(request, "Văn bản đi liên kết chưa được ban hành/số hiệu chưa có. Không thể hoàn thành văn bản đến.")
                return redirect(request.path)

        # cập nhật phân công
        phan_cong.TrangThai = "Hoàn thành"
        phan_cong.save()

        # cập nhật vb đến
        vb.TrangThai = "Hoàn thành"
        vb.save()

        # tạo nhật ký (chỉ 1 record)
        NhatKyCongViec.objects.create(
            PhanCong=phan_cong,
            ThaoTac="Nhân viên báo cáo hoàn thành xử lý văn bản",
            TrangThai="Hoàn thành",
            NguoiThucHien=nhanvien,
            MaVBDen=vb
        )

        # thông báo cho người giao (nếu có)
        if phan_cong.NguoiGiao:
            ThongBao.objects.create(
                TieuDe=f"Văn bản {vb.SoHieu or vb.TrichYeu} đã được báo cáo hoàn thành",
                NoiDung=f"Nhân viên {nhanvien.get_full_name() or nhanvien.username} đã báo cáo hoàn thành xử lý văn bản.",
                MaNhanVien=phan_cong.NguoiGiao,
                MaVBDen=vb
            )

        messages.success(request, f"Văn bản đến '{vb.TrichYeu}' đã được báo cáo hoàn thành.")
        return redirect("danh_sach_van_ban_den")

    # GET -> trả context để template hiển thị thông tin
    context = {
        "vb": vb,
        "vb_di": vb_di,
        "phan_cong": phan_cong,
        "nhanvien": nhanvien,
    }
    context.update(global_notifications(request))
    return render(request, "vanbanden/baocao_vbden.html", context)

@login_required
@permission_required('QLVB.sua_vanbanden', raise_exception=True)
def sua_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, pk=vb_id)
    nhanvien = request.user
    context = {
        'vb': vb,
        'phongbans': PhongBan.objects.all(),
        'nhan_vien_list': User.objects.all().order_by('ho_ten'),
        'DOKHAN_CHOICES': vb._meta.get_field('DoKhan').choices,
        'DOMAT_CHOICES': vb._meta.get_field('DoMat').choices,
    }

    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        now =date.today()

        try:
            # Lấy chuỗi từ form
            ngay_ban_hanh_str = data.get('NgayBanHanh')
            ngay_den_str = data.get('NgayDen')

            # Chuyển sang đối tượng date (chỉ ngày)%m-%d')) if ngay_den_str else None
            ngay_ban_hanh = date.fromisoformat(ngay_ban_hanh_str) if ngay_ban_hanh_str else None
            ngay_den = date.fromisoformat(ngay_den_str) if ngay_den_str else None
        except ValueError:
            messages.error(request,"Lỗi định dạng ngày. Vui lòng nhập theo định dạng ngày/tháng/năm.")
            return render(request, "vanbanden/sua_van_ban_den.html", context)


        if not data.get('TrichYeu') or not data.get('DonViPhatHanh') or not data.get('MaPhongBan'):
            messages.error(request, "Các trường (*) không được để trống.")
            return render(request, "vanbanden/sua_van_ban_den.html", context)

        if ngay_den and ngay_ban_hanh and ngay_den < ngay_ban_hanh:
            messages.error(request, "Ngày đến phải sau ngày phát hành.")
            return render(request, "vanbanden/sua_van_ban_den.html", context)
        if ngay_den and ngay_den > now:
            messages.error(request, "Ngày đến không được lớn hơn hiện tại.")
            return render(request, "vanbanden/sua_van_ban_den.html", context)

        try:
            ma_phong_ban = PhongBan.objects.get(pk=data.get('MaPhongBan'))
        except PhongBan.DoesNotExist:
            messages.error(request, "Phòng ban được chọn không hợp lệ hoặc không tồn tại.")
            return render(request, "vanbanden/sua_van_ban_den.html", context)

        nguoi_trinh_ky = vb.NguoiNhanTrinhKy

        vb.TrichYeu = data.get('TrichYeu')
        vb.LoaiVBDen = data.get('LoaiVBDen')
        vb.DonViPhatHanh = data.get('DonViPhatHanh')
        vb.DoMat = data.get('DoMat')
        vb.DoKhan = data.get('DoKhan')
        vb.YeuCauVBDi = int(data.get('YeuCauVBDi', 0))
        vb.NgayBanHanh = ngay_ban_hanh
        vb.NgayDen = ngay_den  # Đưa vào đây
        vb.NoiDung = data.get('NoiDung')  # Đưa vào đây
        vb.MaPhongBan = ma_phong_ban  # Đưa vào đây
        vb.NguoiNhanTrinhKy = nguoi_trinh_ky  # Đưa vào đây

        file_upload = files.get('FileDinhKem')
        if file_upload:
            if vb.FileDinhKem:
                vb.FileDinhKem.delete(save=False)
            vb.FileDinhKem = file_upload

        try:
            vb.save()

            # --- ĐÃ SỬA: BỎ messages.success VÀ THÊM ?status=success VÀO URL ---
            return redirect(f'{reverse("chi_tiet_vb_den", kwargs={"vb_id": vb.id})}?status=success')

        except Exception as e:
            messages.error(request, f"Lỗi lưu dữ liệu: {e}")
            return render(request, "vanbanden/sua_van_ban_den.html", context)

    NhatKyCongViec.objects.create(
        PhanCong=None,
        ThaoTac="Sửa văn bản đến",
        TrangThai=vb.TrangThai,
        NguoiThucHien=nhanvien,
        MaVBDen=vb
    )

    return render(request, "vanbanden/sua_van_ban_den.html", context)

from django.contrib.auth import logout
from django.shortcuts import redirect

@login_required
@permission_required('QLVB.thongqua_vanbandi', raise_exception=True)
def trang_thong_qua(request, vb_id):
    vb = get_object_or_404(VanBanDi, id=vb_id)
    danh_sach_quan_ly = User.objects.filter(vai_tro="QL")
    truong_phong = request.user

    if request.method == "POST":
        action = request.POST.get("action")
        ly_do = request.POST.get("ly_do_tu_choi", "")
        quan_ly_id = request.POST.get("quan_ly_chon")
        quan_ly = User.objects.filter(id=quan_ly_id).first() if quan_ly_id else None

        if action == "thongqua":
            if not quan_ly:
                messages.error(request, "⚠ Phải chọn quản lý trước khi thông qua.")
                return render(
                    request,
                    "vanbandi/thongqua.html",
                    {"vb": vb, "danh_sach_quan_ly": danh_sach_quan_ly}
                )

            # Lưu chữ ký
            file_chu_ky = request.FILES.get("file_chu_ky")
            if file_chu_ky:
                vb.FileChuKy = file_chu_ky

            # Cập nhật trạng thái văn bản
            vb.TrangThai = "Chờ phê duyệt"
            vb.save()

            phan_cong_moi = PhanCongCongViec.objects.create(
                TieuDe=f"Phê duyệt văn bản đi {vb.SoHieu}",
                MoTa=f"Trưởng phòng {truong_phong.ho_ten} trình phê duyệt văn bản '{vb.TrichYeu}'.",
                NguoiGiao=truong_phong,
                NguoiNhan=quan_ly,
                VanBanDi=vb,
                HanChot=timezone.now() + timezone.timedelta(days=2),
                TrangThai=TrangThaiCongViec.CHO_XET_DUYET
            )

            # Thông báo cho quản lý
            ThongBao.objects.create(
                TieuDe=f"Trình duyệt văn bản '{vb.TrichYeu}'",
                NoiDung=f"Trưởng phòng {truong_phong.ho_ten} trình duyệt văn bản '{vb.TrichYeu}'.",
                MaNhanVien=quan_ly,
                MaVBDi=vb
            )

            # Nhật ký
            NhatKyCongViec.objects.create(
                PhanCong=phan_cong_moi,
                ThaoTac="Thông qua dự thảo",
                TrangThai=vb.TrangThai,
                NguoiThucHien=truong_phong,
                MaVBDi=vb
            )

            messages.success(request, f"Văn bản '{vb.TrichYeu}' đã được trình duyệt.")

        elif action == "tuchoi":
            vb.TrangThai = "Bị từ chối"
            vb.save()

            NhatKyCongViec.objects.create(
                PhanCong=None,
                ThaoTac="Từ chối thông qua dự thảo",
                TrangThai=vb.TrangThai,
                NguoiThucHien=truong_phong,
                MaVBDi=vb
            )

            if vb.MaNhanVien:
                ThongBao.objects.create(
                    TieuDe=f"Dự thảo '{vb.TrichYeu}' bị từ chối",
                    NoiDung=(
                        f"Dự thảo '{vb.TrichYeu}' bị từ chối bởi "
                        f"Trưởng phòng {truong_phong.ho_ten}. "
                        f"Lý do: {ly_do or 'Không ghi rõ'}"
                    ),
                    MaNhanVien=vb.MaNhanVien,
                    MaVBDi=vb
                )

            messages.warning(request, f"Dự thảo '{vb.TrichYeu}' đã bị từ chối.")

        return redirect('vanbandi_detail', vb.id)

    return render(
        request,
        "vanbandi/thongqua.html",
        {"vb": vb, "danh_sach_quan_ly": danh_sach_quan_ly}
    )