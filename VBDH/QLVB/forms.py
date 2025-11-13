<<<<<<< HEAD
# forms.py
from django import forms
from .models import VanBanDen, NhanVien, PhongBan, DOKHAN_CHOICES, DOMAT_CHOICES

from django.utils.safestring import mark_safe


class ReadOnlyWidget(forms.Widget):
    """Widget hiển thị dữ liệu dưới dạng chỉ đọc, không gửi giá trị POST."""

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            display_value = ""
        else:
            # Nếu value là object (như NhanVien), hiển thị __str__ của nó
            display_value = str(value)

            # Tạo input type='hidden' để giữ ID (giá trị thực)
        hidden_input = f'<input type="hidden" name="{name}" value="{value.pk if hasattr(value, "pk") else value}">'

        # Tạo div hiển thị tên (chỉ đọc) với CSS đồng bộ với các ô nhập liệu
        display_div = f"""
            <div class="readonly-display-box" style="
                width: 100%; border: 1px solid #999; padding: 5px; 
                border-radius: 3px; background-color: #eee; box-sizing: border-box;
            ">
                {display_value}
            </div>
        """
        return mark_safe(hidden_input + display_div)

    def value_from_datadict(self, data, files, name):
        # Lấy giá trị thực (PK) từ hidden input
        return data.get(name)

# Định nghĩa ModelForm cho Văn Bản Đến
class VanBanDenForm(forms.ModelForm):
    class Meta:
        model = VanBanDen

        # Danh sách đầy đủ các trường cần hiển thị và chỉnh sửa trên form
        fields = [
            'SoHieu',
            'TrichYeu',
            'LoaiVBDen',
            'DonViPhatHanh',
            'NgayBanHanh',
            'NgayDen',
            'MaPhongBan',
            'MaNhanVien',  # Trường đã chọn để tự chọn trong form
            'NguoiNhanTrinhKy',  # Trường NguoiNhanTrinhKy (nếu có)
            'NoiDung',
            'DoKhan',
            'DoMat',
            'TrangThai',
            'FileDinhKem',
        ]

        # Định nghĩa Widgets cho các trường ngày/giờ
        widgets = {
            # Sử dụng datetime-local cho input ngày giờ
            'NgayBanHanh': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'NgayDen': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),

            # Tùy chọn: Sử dụng Textarea cho các trường có nội dung lớn
            'TrichYeu': forms.Textarea(attrs={'rows': 2}),
            'NoiDung': forms.Textarea(attrs={'rows': 3}),
        }

        # Định nghĩa Labels tiếng Việt có dấu
        labels = {
            'SoHieu': 'Số hiệu (*)',
            'TrichYeu': 'Trích yếu (*)',
            'LoaiVBDen': 'Loại văn bản:',
            'DonViPhatHanh': 'Đơn vị phát hành (*)',
            'NgayBanHanh': 'Ngày ban hành:',
            'NgayDen': 'Ngày đến:',
            'MaPhongBan': 'Phòng ban nhận:',
            'MaNhanVien': 'Nhân viên tạo:',
            'NguoiNhanTrinhKy': 'Người nhận trình ký:',
            'NoiDung': 'Nội dung:',
            'DoKhan': 'Độ khẩn:',
            'DoMat': 'Độ mật:',
            'TrangThai': 'Trạng thái:',
            'FileDinhKem': 'Tệp đính kèm:',
        }

    # Cần định nghĩa __init__ để đảm bảo định dạng ngày tháng đầu vào được xử lý đúng
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Định dạng input cho các trường DateTime
        self.fields['NgayBanHanh'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
        self.fields['NgayDen'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']

        # Tùy chọn: Đặt queryset cho các trường ForeignKey nếu bạn muốn lọc
        # self.fields['MaNhanVien'].queryset = NhanVien.objects.filter(...)
        # self.fields['MaPhongBan'].queryset = PhongBan.objects.all()

        # Thêm CSS class cho các trường Select/Input để đồng bộ giao diện
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.TextInput, forms.Textarea, forms.DateTimeInput)):
                field.widget.attrs.update({'class': 'form-control-style'})
=======
from django import forms
from .models import VanBanDi


class VanBanDiEditForm(forms.ModelForm):
    """Form chỉnh sửa văn bản đi"""
    class Meta:
        model = VanBanDi
        fields = [
            "SoHieu",
            "TrichYeu",
            "NoiDung",
            "DonViNhan",
            "Email",
            "FileDinhKem",
            "DoMat",
            "DoKhan"
        ]

        widgets = {
            "SoHieu": forms.TextInput(attrs={"class": "form-control"}),
            "TrichYeu": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "NoiDung": forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
            "DonViNhan": forms.TextInput(attrs={"class": "form-control"}),
            "Email": forms.EmailInput(attrs={"class": "form-control"}),
            "DoMat": forms.TextInput(attrs={"class": "form-control"}),
            "DoKhan": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nếu model có các trường này, bạn có thể khóa lại khi chỉnh sửa
        if "LoaiVbDi" in self.fields:
            self.fields["LoaiVbDi"].disabled = True
        if "NgayBanHanh" in self.fields:
            self.fields["NgayBanHanh"].disabled = True

    def clean_FileDinhKem(self):
        """Kiểm tra file hợp lệ khi chỉnh sửa"""
        file = self.cleaned_data.get("FileDinhKem", None)
        if file:
            ext = file.name.lower().split('.')[-1]
            if ext not in ["pdf", "jpg", "png"]:
                raise forms.ValidationError("Chỉ chấp nhận file .pdf, .jpg hoặc .png.")
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError("Dung lượng file không vượt quá 20MB.")
        return file


class VanBanDiForm(forms.ModelForm):
    """Form tạo mới văn bản đi"""
    class Meta:
        model = VanBanDi
        fields = [
            "SoHieu",
            "TrichYeu",
            "LoaiVbDi",
            "DonViNhan",
            "Email",
            "NoiDung",
            "FileDinhKem",
            "NgayBanHanh",
            "DoMat",
            "DoKhan",
            "MaVBDen",
        ]

        widgets = {
            "SoHieu": forms.TextInput(attrs={"class": "form-control"}),
            "TrichYeu": forms.Textarea(attrs={"rows": 2, "maxlength": "500", "class": "form-control"}),
            "LoaiVbDi": forms.TextInput(attrs={"class": "form-control"}),
            "DonViNhan": forms.TextInput(attrs={"class": "form-control"}),
            "Email": forms.EmailInput(attrs={"class": "form-control"}),
            "NoiDung": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "NgayBanHanh": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "DoMat": forms.TextInput(attrs={"class": "form-control"}),
            "DoKhan": forms.TextInput(attrs={"class": "form-control"}),
            "MaVBDen": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_FileDinhKem(self):
        """Kiểm tra file hợp lệ khi tạo mới"""
        file = self.cleaned_data.get("FileDinhKem", None)
        if file:
            ext = file.name.lower().split('.')[-1]
            if ext not in ["pdf", "jpg", "png"]:
                raise forms.ValidationError("Chỉ chấp nhận file .pdf, .jpg hoặc .png.")
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError("Dung lượng file không vượt quá 20MB.")
        return file
>>>>>>> 7c60d542c1276cc3b32265b285a016f95abd40f8
