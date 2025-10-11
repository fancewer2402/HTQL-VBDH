from django.urls import path
from . import views

urlpatterns = [
    path('logout/', views.logout_confirm, name='logout_confirm'),
    path('tra-cuu-van-ban/', views.tra_cuu_van_ban, name='tra_cuu_van_ban'),
    path('tra-cuu-van-ban/', views.tra_cuu_van_ban, name='tra_cuu_van_ban'),
]
