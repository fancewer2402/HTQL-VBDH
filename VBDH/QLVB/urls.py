from django.urls import path
from django.contrib import admin
from . import views
# from ..VBDH import urls

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('tra-cuu-van-ban/', views.tra_cuu_van_ban, name='tra_cuu_van_ban'),
    path('taovanbanden/', views.them_van_ban, name='them_van_ban'),
    path('vanbandi/', views.ds_vanbandi, name='vanbandi'),
    path('vanbandi/<int:pk>/', views.vanbandi_detail, name='vanbandi_detail'),
    path('taoduthao/', views.tao_du_thao, name='tao_du_thao'),
    path('vanbanden/', views.danh_sach_van_ban_den, name='danh_sach_van_ban_den'),
    path('vanbanden/<int:vb_id>/', views.chi_tiet_vb_den, name='chi_tiet_vb_den'),
    path('xetduyetvanbandi/<int:id>/', views.xetduyetvanbandi, name='xetduyetvanbandi'),
    path('<str:loaivanban>/<int:vanban_id>/nhatkyhoatdong/', views.nhat_ky_hoat_dong, name='nhatkyhoatdong'),
    path('phancong/<int:id>/', views.phan_cong_van_thu, name='phancongvanthu'),
]