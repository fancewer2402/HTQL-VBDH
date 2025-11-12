import os
from django import template

register = template.Library()

@register.filter
def filename(value):
    """Trả về tên tệp tin từ đường dẫn đầy đủ."""
    if value and hasattr(value, 'name'):
        return os.path.basename(value.name)
    return value