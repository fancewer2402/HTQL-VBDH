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
from .models import VanBanDi, VanBanDen, ThongBao, NhatKyCongViec, PhongBan, PhanCongCongViec
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

            # DÙ LÀ QUẢN LÝ, VĂN THƯ, NHÂN VIÊN HAY TRƯỞNG PHÒNG
            # → ĐỀU VÀO DANH SÁCH VĂN BẢN ĐẾN LUÔN!!!
            return redirect('danh_sach_van_ban_den')  # ← ĐÂY LÀ DÒNG CON MUỐN

            # Nếu sau này muốn phân dashboard theo role thì bỏ comment lại đoạn dưới
            # if user.groups.filter(name='Quản lý').exists():
            #     return redirect('dashboard_quanly')
            # elif user.groups.filter(name='Văn thư').exists():
            #     return redirect('dashboard_vanthu')
            # else:
            #     return redirect('dashboard_nhanvien')
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
def them_van_ban(request):
    context = {
        'phong_ban_list': PhongBan.objects.all(),
        'nhan_vien_list': User.objects.filter(vai_tro='QL').order_by('ho_ten'),
        'DOKHAN_CHOICES': DOKHAN_CHOICES,
        'DOMAT_CHOICES': DOMAT_CHOICES,
        'loai_vb_list': VanBanDen.objects.values_list('LoaiVBDen', flat=True).distinct().order_by('LoaiVBDen'),
        'so_hieu_tu_dong': get_so_hieu_tu_dong(),
        'initial_data': {},
    }

    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        now = timezone.now()
        context['initial_data'] = dict(data.items())

        # Xử lý Ngày/Giờ
        try:
            ngay_ban_hanh_str = data.get('NgayBanHanh')
            ngay_den_str = data.get('NgayDen')

            if not ngay_ban_hanh_str or not ngay_den_str:
                raise ValueError("Ngày phát hành và Ngày đến không được để trống.")

            # Chuyển string 'YYYY-MM-DD' sang date object
            ngay_ban_hanh = date.fromisoformat(ngay_ban_hanh_str)
            ngay_den = date.fromisoformat(ngay_den_str)

        except ValueError:
            messages.error(request, "Lỗi định dạng Ngày/Giờ. Vui lòng kiểm tra lại.")
            return render(request, "vanbanden/create.html", context)

        # Kiểm tra logic ngày
        today = date.today()
        if ngay_den < ngay_ban_hanh:
            messages.error(request, "Ngày đến phải lớn hơn hoặc bằng ngày ban hành.")
            return render(request, "vanbanden/create.html", context)

        if ngay_den > today:
            messages.error(request, "Ngày đến không được lớn hơn ngày hôm nay.")
            return render(request, "vanbanden/create.html", context)
        if not data.get('MaPhongBan'):
            messages.info(request, "Vui lòng chọn Phòng ban")
            return render(request, "vanbanden/create.html", context)
        trich_yeu = data.get('TrichYeu', '').strip()
        if len(trich_yeu) <= 5:
            messages.error(request, "Trích yếu phải lớn hơn 5 ký tự.")
            return render(request, "vanbanden/create.html", context)
        # Lấy Foreign Key
        ma_nhan_vien = request.user
        ma_phong_ban = get_object_or_404(PhongBan, pk=data.get('MaPhongBan'))

        nguoi_trinh_ky = None
        if data.get('NguoiNhanTrinhKy'):
            try:
                nguoi_trinh_ky = User.objects.get(id=data.get('NguoiNhanTrinhKy'), vai_tro='QL')
            except User.DoesNotExist:
                messages.error(request, "Người nhận trình ký phải là quản lý.")
                return render(request, "vanbanden/create.html", context)

        # Lấy giá trị khác
        do_khan = data.get('DoKhan', 'BINH THUONG')
        do_mat = data.get('DoMat', 'BINH THUONG')
        yeu_cau_vbdi = int(data.get('YeuCauVBDi', 0))

        # Tạo đối tượng VanBanDen
        vb = VanBanDen(
            SoHieu=get_so_hieu_tu_dong(),
            TrichYeu=trich_yeu,
            LoaiVBDen=data.get('LoaiVBDen'),
            DonViPhatHanh=data.get('DonViPhatHanh'),
            NgayBanHanh=ngay_ban_hanh,
            NgayDen=ngay_den,
            NoiDung=data.get('NoiDung'),
            DoKhan=do_khan,
            DoMat=do_mat,
            YeuCauVBDi=yeu_cau_vbdi,
            MaNhanVien=ma_nhan_vien,
            MaPhongBan=ma_phong_ban,
            NguoiNhanTrinhKy=nguoi_trinh_ky,
        )

        # Xử lý File đính kèm (Logic này là đúng)
        file_upload = request.FILES.get('FileDinhKem')
        if file_upload:
            vb.FileDinhKem = file_upload

        vb.save()
        from django.urls import reverse
        return redirect(f'{reverse("danh_sach_van_ban_den")}?status=create_success')

    return render(request, "vanbanden/create.html", context)

def ds_vanbandi(request):
    # CẬP NHẬT: Sắp xếp ưu tiên theo NgayTao giảm dần (-NgayTao) để văn bản mới tạo luôn nằm trên cùng.
    # NgayBanHanh (-NgayBanHanh) được sử dụng làm sắp xếp phụ.
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
        is_manager_role = current_user.vai_tro in ['TP']
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
        if current_user.vai_tro == "QL" and van_ban.TrangThai == "Chờ xét duyệt":
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


def sua_vanbandi(request, id):
    vb = get_object_or_404(VanBanDi, id=id)

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
    return render(request, "vanbandi/sua_vanbandi.html", {"form": form, "vb": vb})


def chi_tiet_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, id=vb_id)
    if vb.TrangThai == 'CHỜ XÉT DUYỆT':
        return redirect('xet_duyet_vb_den', vb_id=vb_id)

        # 2. Trạng thái: CHỜ XÁC NHẬN -> Điều hướng tới trang Xác Nhận Công Việc
    elif vb.TrangThai == 'CHỜ XÁC NHẬN':
        # Lưu ý: Nếu URL name của bạn là phan_cong_nhan_vien_vbden, bạn cần truyền id
        # Nhưng dựa trên URL bạn cung cấp (vanbanden/xacnhan/<int:vb_id>/), thì vb_id là đúng
        return redirect('xac_nhan_phan_cong_vbden', vb_id=vb_id)

        # 3. Trạng thái: CHỜ XỬ LÝ -> Điều hướng tới trang Báo cáo/Hoàn thành
    elif vb.TrangThai == 'CHỜ XỬ LÝ':
        return redirect('bao_cao_vbden', vb_id=vb_id)

        # Trường hợp mặc định (Đã hoàn thành, Bị từ chối, Đang lưu hành, v.v.)
        # Nếu không có redirect nào được thực thi, hàm sẽ chạy đến đây và render trang chi tiết
    context = {
        'vb': vb,
        # ... Thêm dữ liệu context khác nếu cần thiết (ví dụ: danh sách lịch sử xử lý)
    }
    return render(request, 'vanbanden/chi_tiet_vb_den.html', context)


@login_required
@permission_required('QLVB.tao_vanbandi', raise_exception=True)
def tao_du_thao(request):
    """Nhân viên tạo dự thảo và trình duyệt lên Trưởng phòng."""
        # ⚙️ Giả sử nhân viên đang đăng nhập
    nhanvien = request.user
    count = VanBanDi.objects.count() + 1
    so_hieu_tu_dong = f"VB-{datetime.now().year}-{count:04d}"

        # ✅ Tạo văn bản mới

    danh_sach_yeu_cau_list = VanBanDen.objects.filter(
        TrangThai='Đang xử lý',
        YeuCauVBDi=1  # chỉ lấy những văn bản có yêu cầu
    )
    if request.method == "POST":
        ma_phong_ban_id = request.POST.get('MaPhongBan')
        MaVBDen_id = request.POST.get("MaVanBanDen")
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
            MaVBDen_id=request.POST.get("MaVanBanDen"),
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

        NhatKyCongViec.objects.create(
            PhanCong=None,  # hoặc đối tượng PhanCongCongViec nếu có
            ThaoTac="Tạo văn bản đi",
            TrangThai=vb.TrangThai,
            NguoiThucHien=nhanvien,
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
                TieuDe=f"Phân công văn bản: {vb.SoHieu}",
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
                NguoiThucHien=quanly
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

               NhatKyCongViec.objects.create(
                   PhanCong=None,
                   ThaoTac="Ban hành",
                   TrangThai=vb.TrangThai,
                   NguoiThucHien=request.user
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
    user = request.user
    role = user.vai_tro

    # --- 1. Lọc theo vai trò ---
    if role == "VT":  # Văn thư chỉ xem văn bản mình tạo
        van_ban_list = VanBanDen.objects.filter(
            MaNhanVien=user
        ).order_by("-NgayTao")

    elif role == "NV":  # Nhân viên chỉ xem văn bản được phân công
        van_ban_list = VanBanDen.objects.filter(
            phancongcongviec__NguoiNhan=user
        ).distinct().order_by("-NgayTao")

    else:  # QL hoặc Trưởng phòng: xem tất cả
        van_ban_list = VanBanDen.objects.all().order_by("-NgayTao")
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
    from_date = request.GET.get('from_date') or ''
    to_date = request.GET.get('to_date') or ''
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

@login_required
@permission_required('QLVB.sua_vanbanden', raise_exception=True)
def sua_vb_den(request, vb_id):
    vb = get_object_or_404(VanBanDen, pk=vb_id)
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

    return render(request, "vanbanden/sua_van_ban_den.html", context)

from django.contrib.auth import logout
from django.shortcuts import redirect

def trang_thong_qua(request, vb_id):
    vb = get_object_or_404(VanBanDi, id=vb_id)
    danh_sach_quan_ly = User.objects.filter(vai_tro="QL")  # Lấy tất cả quản lý
    truong_phong = request.user

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
            NhatKyCongViec.objects.create(
                PhanCong=None,  # hoặc đối tượng PhanCongCongViec nếu có
                ThaoTac="Thông qua",
                TrangThai=vb.TrangThai,
                NguoiThucHien=truong_phong
            )
            messages.success(request, f" Văn bản '{vb.TrichYeu}' đã được trình duyệt.")

        elif action == "tuchoi":
            vb.TrangThai = "Bị từ chối"
            vb.save()

            NhatKyCongViec.objects.create(
                PhanCong=None,
                ThaoTac="Thông qua",
                TrangThai=vb.TrangThai,
                NguoiThucHien=truong_phong
            )

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