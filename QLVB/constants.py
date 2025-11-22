# QLVB/constants.py
from django.db import models


class TrangThaiCongViec(models.TextChoices):
    CHO_XET_DUYET = "Chờ xét duyệt", "CHỜ XÉT DUYỆT"
    BI_TU_CHOI = "Bị từ chối", "BỊ TỪ CHỐI"
    CHO_PHAN_CONG = "Chờ phân công", "CHỜ PHÂN CÔNG"
    CHO_XAC_NHAN = "Chờ xác nhận", "CHỜ XÁC NHẬN"
    DANG_XU_LY = "Đang xử lý", "ĐANG XỬ LÝ"
    HOAN_THANH = "Hoàn thành", "HOÀN THÀNH"
    CHO_BAN_HANH = "Chờ ban hành", "CHỜ BAN HÀN"
    DA_BAN_HANH = "Đã ban hành", "ĐÃ BAN HÀN"


# Các hằng số khác bạn có thể thêm sau này ở đây
DOKHAN_CHOICES = [
    ('KHAN', 'Khẩn'),
    ('BINH THUONG', 'Bình thường'),
    ('HOA TOC', 'Hỏa tốc'),
]

DOMAT_CHOICES = [
    ('MAT', 'Mật'),
    ('TOI MAT', 'Tối mật'),
    ('BINH THUONG', 'Bình thường'),
]

DO_KHAN_VBDI_CHOICES = [
    ('BINH THUONG', 'Bình thường'),
    ('KHAN', 'Khẩn'),
    ('HOA TOC', 'Hỏa tốc'),
]

DO_MAT_VBDI_CHOICES = [
    ('BINH THUONG', 'Bình thường'),
    ('MAT', 'Mật'),
    ('TOI MAT', 'Tối mật'),
]