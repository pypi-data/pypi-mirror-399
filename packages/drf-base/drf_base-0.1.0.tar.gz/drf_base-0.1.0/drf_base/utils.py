from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status

import hashlib
import secrets
import string


def generate_random_string(length=12):
    """生成随机字符串"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_md5(text):
    """生成 MD5 哈希值"""
    return hashlib.md5(text.encode()).hexdigest()


def get_client_ip(request):
    """获取客户端 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """格式化日期时间"""
    if dt is None:
        return None
    return dt.strftime(format_str)


def get_today():
    """获取今天的日期"""
    return timezone.now().date()


def get_now():
    """获取当前时间"""
    return timezone.now()


def validate_positive(value, field_name='value'):
    """验证值是否为正数"""
    if value <= 0:
        raise ValidationError(f'{field_name} 必须是正数')
    return value


def validate_min_length(value, min_length, field_name='value'):
    """验证字符串最小长度"""
    if len(value) < min_length:
        raise ValidationError(f'{field_name} 长度不能小于 {min_length}')
    return value


def validate_max_length(value, max_length, field_name='value'):
    """验证字符串最大长度"""
    if len(value) > max_length:
        raise ValidationError(f'{field_name} 长度不能超过 {max_length}')
    return value


def create_success_response(data=None, message='操作成功'):
    """创建成功响应（保持 DRF 原始响应结构）"""
    return Response(data, status=status.HTTP_200_OK)


def create_error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    """创建错误响应（保持 DRF 原始响应结构）"""
    return Response({'detail': message}, status=status_code)


def create_paginated_response(queryset, serializer_class, request, view=None):
    """创建分页响应（使用 DRF 内置分页）"""
    from rest_framework.pagination import PageNumberPagination
    
    pagination = PageNumberPagination()
    paginated_queryset = pagination.paginate_queryset(queryset, request, view=view)
    serializer = serializer_class(paginated_queryset, many=True)
    return pagination.get_paginated_response(serializer.data)
