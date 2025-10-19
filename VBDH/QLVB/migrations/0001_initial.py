import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PhongBan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TenPhongBan', models.CharField(max_length=100, unique=True)),
                ('Email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='NhanVien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('HoTen', models.CharField(max_length=100)),
                ('VaiTro', models.CharField(blank=True, choices=[('NV', 'Nhân Viên'), ('QL', 'Quản Lý'), ('VT', 'Văn Thư'), ('TP', 'Trưởng Phòng')], max_length=100, null=True)),
                ('Email', models.EmailField(max_length=254, unique=True)),
                ('SDT', models.CharField(max_length=10)),
                ('PhongBan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nhan_viens', to='QLVB.phongban')),
            ],
        ),
        migrations.CreateModel(
            name='VanBanDen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SoHieu', models.CharField(max_length=100)),
                ('TrichYeu', models.CharField(max_length=250)),
                ('LoaiVBDen', models.CharField(max_length=100)),
                ('DonViPhatHanh', models.CharField(max_length=250)),
                ('NgayBanHanh', models.DateTimeField()),
                ('NgayDen', models.DateTimeField()),
                ('NoiDung', models.CharField(max_length=250)),
                ('DoKhan', models.CharField(choices=[('KHAN', 'Khẩn'), ('BINH THUONG', 'Bình thường')], default='BINH THUONG', max_length=50)),
                ('DoMat', models.CharField(choices=[('MAT', 'Mật'), ('BINH THUONG', 'Bình thường')], default='BINH THUONG', max_length=50)),
                ('FileDinhKem', models.FileField(blank=True, upload_to='vanbanden/')),
                ('MaNhanVien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.nhanvien')),
                ('MaPhongBan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.phongban')),
            ],
        ),
        migrations.CreateModel(
            name='VanBanDi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SoHieu', models.CharField(max_length=50, unique=True)),
                ('NgayBanHanh', models.DateField(blank=True, null=True)),
                ('TrichYeu', models.CharField(max_length=255)),
                ('NoiDung', models.TextField()),
                ('LoaiVbDi', models.CharField(max_length=255)),
                ('DonViNhan', models.CharField(blank=True, max_length=255, null=True)),
                ('Email', models.EmailField(max_length=254)),
                ('FileDinhKem', models.FileField(blank=True, upload_to='vanbandi/')),
                ('DoMat', models.CharField(blank=True, max_length=255, null=True)),
                ('DoKhan', models.CharField(blank=True, max_length=255, null=True)),
                ('TrangThai', models.CharField(blank=True, max_length=255, null=True)),
                ('NgayTao', models.DateTimeField(auto_now_add=True)),
                ('MaNhanVien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.nhanvien')),
            ],
        ),
        migrations.CreateModel(
            name='ThongBao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TieuDe', models.TextField()),
                ('NgayTao', models.DateTimeField(auto_now_add=True)),
                ('MaNhanVien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.nhanvien')),
                ('MaVBDen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.vanbanden')),
                ('MaVBDi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.vanbandi')),
            ],
        ),
        migrations.CreateModel(
            name='NhatKyCongVien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TieuDe', models.CharField(max_length=100)),
                ('MoTa', models.TextField(max_length=250)),
                ('ThaoTac', models.TextField()),
                ('TrangThai', models.CharField(choices=[('Chờ xét duyêt', 'CHỜ XÉT DUYỆT'), ('Bị từ chối', 'BỊ TỪ CHỐI'), ('Chờ phân công', 'CHỜ PHÂN CÔNG'), ('Chờ xác nhận', 'CHỜ XÁC NHẬN'), ('Đang xử lý', 'ĐANG XỬ LÝ'), ('Hoàn thành', 'HOÀN THÀNH'), ('Chờ ban hành', 'CHỜ BAN HÀNH'), ('Đã ban hành', 'ĐÃ BAN HÀNH')], max_length=50)),
                ('NgayTao', models.DateTimeField(auto_now_add=True)),
                ('HanChot', models.DateTimeField()),
                ('MaNhanVien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.nhanvien')),
                ('MaVBDen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.vanbanden')),
                ('MaVBDi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='QLVB.vanbandi')),
            ],
        ),
    ]
