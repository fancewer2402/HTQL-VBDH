from django import forms
from .models import VanBanDi

class VanBanDiEditForm(forms.ModelForm):
    """Form chỉnh sửa văn bản đi"""
    class Meta:
        model = VanBanDi
        fields = [
            "SoHieu", "TrichYeu", "NoiDung", "DonViNhan",
            "Email", "FileDinhKem", "DoMat", "DoKhan"
        ]
        widgets = {
            "TrichYeu": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "NoiDung": forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
            "SoHieu": forms.TextInput(attrs={"class": "form-control"}),
            "DonViNhan": forms.TextInput(attrs={"class": "form-control"}),
            "Email": forms.EmailInput(attrs={"class": "form-control"}),
            "DoMat": forms.TextInput(attrs={"class": "form-control"}),
            "DoKhan": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nếu cần khóa các trường không được chỉnh
        if "LoaiVbDi" in self.fields:
            self.fields["LoaiVbDi"].disabled = True
        if "NgayBanHanh" in self.fields:
            self.fields["NgayBanHanh"].disabled = True


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
        file = self.cleaned_data.get("FileDinhKem", None)
        if file:
            ext = file.name.lower().split('.')[-1]
            if ext not in ["pdf", "jpg", "png"]:
                raise forms.ValidationError("Chỉ chấp nhận file định dạng .pdf, .jpg, hoặc .png.")
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError("Dung lượng file không vượt quá 20MB.")
        return file
