from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .pagination import DefaultPagination

# 检测 django-filter 是否安装
try:
    from django_filters.rest_framework import DjangoFilterBackend
    DJANGO_FILTER_AVAILABLE = True
except ImportError:
    DJANGO_FILTER_AVAILABLE = False


class BaseModelViewSet(viewsets.ModelViewSet):
    pagination_class = DefaultPagination
    
    # 动态设置 filter_backends
    @classmethod
    def get_filter_backends(cls):
        filter_backends = [OrderingFilter, SearchFilter]
        if DJANGO_FILTER_AVAILABLE:
            filter_backends.append(DjangoFilterBackend)
        return filter_backends
    
    filter_backends = property(get_filter_backends)
