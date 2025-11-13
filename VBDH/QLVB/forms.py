from django import forms
from django.utils import timezone
from .models import VanBanDi, PhongBan, VanBanDen

class VanBanDiForm(forms.ModelForm):
    # Thêm trường Mã văn bản đến
    MaVBDen = forms.ModelChoiceField(
        queryset=VanBanDen.objects.all(),
        required=False,
        empty_label="-- Danh sách yêu cầu --",
        label="Mã văn bản đến"
    )

    class Meta:
        model = VanBanDi
        fields = [
            'PhongBan',       # Phòng ban
            'TrichYeu',       # Trích yếu
            'LoaiVbDi',       # Loại văn bản đi
            'DonViNhan',      # Đơn vị nhận
            'MaVBDen',        # Mã văn bản đến
            'NoiDung',        # Nội dung
            'Email',          # Email
            'FileDinhKem',    # File đính kèm
            'DoMat',          # Độ mật
            'DoKhan',         # Độ khẩn
            'TrangThai',      # Trạng thái
            'NgaySoanThao',   # Ngày soạn thảo
        ]

        widgets = {
            'NoiDung': forms.Textarea(attrs={'rows': 5}),
            'Email': forms.EmailInput(attrs={'placeholder': 'Nhập email người nhận'}),
            'DoMat': forms.TextInput(attrs={'placeholder': 'Ví dụ: Bình thường, Mật'}),
            'DoKhan': forms.TextInput(attrs={'placeholder': 'Ví dụ: Thường, Khẩn'}),
            'NgaySoanThao': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dropdown Phòng ban
        self.fields['PhongBan'].queryset = PhongBan.objects.all()
        self.fields['PhongBan'].empty_label = "-- Chọn phòng ban --"

        # Mặc định ngày soạn thảo là hôm nay nếu tạo mới
        if not self.instance.pk:
            self.fields['NgaySoanThao'].initial = timezone.now().date()

        # Ẩn trường trạng thái, đặt mặc định là "Chờ phê duyệt"
        self.fields['TrangThai'].widget = forms.HiddenInput()
        self.fields['TrangThai'].initial = "Chờ phê duyệt"

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Đảm bảo trạng thái luôn là Chờ phê duyệt khi tạo mới
        if not instance.TrangThai:
            instance.TrangThai = "Chờ phê duyệt"
        if commit:
            instance.save()
        return instance
