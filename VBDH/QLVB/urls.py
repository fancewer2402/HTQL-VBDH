from django.urls import path
from django.contrib import admin
from . import views
# from ..VBDH import urls

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('tra-cuu-van-ban/', views.tra_cuu_van_ban, name='tra_cuu_van_ban'),

]
