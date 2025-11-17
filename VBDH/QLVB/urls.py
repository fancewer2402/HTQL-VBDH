from django.urls import path
from . import views

urlpatterns = [
    # === XÁC THỰC ===
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # === VĂN BẢN ĐẾN ===
    path('taovanbanden/', views.them_van_ban, name='them_van_ban'),
    path('vanbanden/', views.danh_sach_van_ban_den, name='danh_sach_van_ban_den'),
    path('vanbanden/<int:vb_id>/', views.chi_tiet_vb_den, name='chi_tiet_vb_den'),
    path('vanbanden/xetduyet/<int:vb_id>/', views.xet_duyet_vb_den, name='xet_duyet_vb_den'),
    path('vanbanden/phancong/<int:id>/', views.phan_cong_nhan_vien_vbden, name='phan_cong_nhan_vien_vbden'),
    path('vanbanden/xacnhan/<int:vb_id>/', views.xac_nhan_phan_cong_vbden, name='xac_nhan_phan_cong_vbden'),
    path('vanbanden/baocao/<int:vb_id>/', views.bao_cao_vbden, name='bao_cao_vbden'),
    path('sua/<int:vb_id>/', views.sua_vb_den, name='sua_vb_den'),

    # === VĂN BẢN ĐI ===
    path('vanbandi/', views.ds_vanbandi, name='vanbandi'),  # Danh sách + tìm kiếm
    path('vanbandi/<int:pk>/', views.vanbandi_detail, name='vanbandi_detail'),
    path('vanbandi/ban-hanh/<int:id>/', views.ban_hanh_van_ban, name='ban_hanh_van_ban'),
    path('suavanbandi/<int:id>/', views.sua_vanbandi, name='sua_vanbandi'),
    path('xetduyetvanbandi/<int:id>/', views.xetduyetvanbandi, name='xetduyetvanbandi'),
    path('taoduthao/', views.tao_du_thao, name='tao_du_thao'),
    path('vanbandi/<int:id>/sua/', views.sua_vanbandi, name='sua_vanbandi'),  # trùng tên, giữ 1
    path('vanbandi/<int:vb_id>/thong-qua/', views.trang_thong_qua, name='thong_qua_van_ban'),

    # === PHÂN CÔNG & NHẬT KÝ ===
    path('<str:loaivanban>/<int:vanban_id>/nhatkyhoatdong/', views.nhat_ky_hoat_dong, name='nhatkyhoatdong'),
    path('phancong/<int:id>/', views.phan_cong_van_thu, name='phancongvanthu'),

    # === TRA CỨU ===
    path('tra-cuu-van-ban/', views.tra_cuu_van_ban, name='tra_cuu_van_ban'),

    # === THÔNG BÁO ===
    path('thongbao/doc/<int:id>/', views.mark_notification_read, name='mark_notification_read'),
    path('thongbao/read/<int:id>/', views.mark_notification_read, name='mark_notification_read'),  # giữ cả 2
    path('notification/<int:id>/read/', views.mark_notification_read, name='mark_notification_read'),
]