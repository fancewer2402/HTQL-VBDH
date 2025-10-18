from django.urls import path
from django.contrib import admin
from . import views
# from ..VBDH import urls

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_confirm, name='logout_confirm'),
    path('tra-cuu-van-ban/', views.tra_cuu_van_ban, name='tra_cuu_van_ban'),
    path('tra-cuu-van-ban/', views.tra_cuu_van_ban, name='tra_cuu_van_ban'),
    path('logout/', views.logout_confirm, name='logout_confirm'),
    path('logout-success/', views.logout_success, name='logout_success'),
    path('taoduthao/', views.tao_du_thao, name='tao_du_thao'),
]
