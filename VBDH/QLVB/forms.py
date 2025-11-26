# QLVB/forms.py

from django import forms
from .models import VanBanDi


class VanBanDiEditForm(forms.ModelForm):
    """Form chỉnh sửa văn bản đi (Cập nhật logic clean để tránh lỗi lưu)"""

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
            "DoKhan",
            "LoaiVbDi",
            "NgayBanHanh",
        ]

        widgets = {
            "SoHieu": forms.TextInput(attrs={"class": "form-control"}),
            "TrichYeu": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "NoiDung": forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
            "DonViNhan": forms.TextInput(attrs={"class": "form-control"}),
            "Email": forms.EmailInput(attrs={"class": "form-control"}),
            "DoMat": forms.Select(attrs={"class": "form-control"}),
            "DoKhan": forms.Select(attrs={"class": "form-control"}),
            "LoaiVbDi": forms.TextInput(attrs={"class": "form-control"}),
            "NgayBanHanh": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Đặt các trường sau là không bắt buộc ở form chỉnh sửa để logic clean có thể xử lý
        self.fields["SoHieu"].required = False
        self.fields["Email"].required = False
        self.fields["NgayBanHanh"].required = False
        # Các trường Model bắt buộc (blank=False) phải được handle trong clean()

    def clean(self):
        """Xử lý giữ lại giá trị cũ cho các trường Model yêu cầu (như Email, TrichYeu)"""
        cleaned_data = super().clean()

        if self.instance:
            # Các trường bắt buộc trong Model (blank=False)
            required_fields = ['TrichYeu', 'NoiDung', 'Email']
            # Các trường có thể giữ lại giá trị cũ
            optional_fields = ['SoHieu', 'NgayBanHanh', 'DonViNhan', 'LoaiVbDi']

            for field_name in required_fields + optional_fields:
                if field_name not in cleaned_data:
                    continue

                new_value = cleaned_data.get(field_name)
                old_value = getattr(self.instance, field_name, None)

                # Trường hợp đặc biệt: NgayBanHanh có thể là date
                if field_name == 'NgayBanHanh' and new_value == '':
                    new_value = None

                # Nếu giá trị mới trống (None, rỗng, False), và có giá trị cũ, thì giữ lại giá trị cũ
                if not new_value and old_value:
                    cleaned_data[field_name] = old_value

        return cleaned_data

    def clean_FileDinhKem(self):
        """Kiểm tra file hợp lệ khi chỉnh sửa"""
        file = self.cleaned_data.get("FileDinhKem", None)

        # Nếu không upload file mới, giữ file cũ
        if not file and self.instance and self.instance.FileDinhKem:
            return self.instance.FileDinhKem

        if file:
            filename = getattr(file, "name", "")
            ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
            allowed = ["pdf", "jpg", "jpeg", "png"]
            if ext not in allowed:
                raise forms.ValidationError("Chỉ chấp nhận file .pdf, .jpg, .jpeg hoặc .png.")
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
            "DoMat": forms.Select(attrs={"class": "form-control"}),
            "DoKhan": forms.Select(attrs={"class": "form-control"}),
            "MaVBDen": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # SoHieu không bắt buộc khi tạo dự thảo
        self.fields["SoHieu"].required = False

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