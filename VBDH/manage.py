#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
# Thêm thư viện 'pathlib' để làm việc với đường dẫn file một cách linh hoạt
from pathlib import Path


def main():
    """Run administrative tasks."""

    # === BỔ SUNG KHẮC PHỤC LỖI MODULE NOT FOUND ===
    # Lấy đường dẫn tuyệt đối của thư mục chứa manage.py (VBDH)
    current_dir = Path(__file__).resolve().parent

    # Lấy đường dẫn tuyệt đối của thư mục cha (HTQL-VBDH)
    project_root = current_dir.parent

    # Thêm thư mục cha (HTQL-VBDH) vào sys.path để Python có thể tìm thấy VBDH
    # khi chạy lệnh từ bên trong thư mục VBDH
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Nếu đang chạy từ thư mục cha (HTQL-VBDH) bằng python VBDH/manage.py
    # thì không cần sửa đổi thêm, vì HTQL-VBDH đã có trong sys.path.
    # =========================================================

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VBDH.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()