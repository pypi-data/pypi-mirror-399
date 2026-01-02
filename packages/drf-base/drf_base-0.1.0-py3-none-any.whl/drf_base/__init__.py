# 导出 pagination 模块
from .pagination import DefaultPagination

# 导出 viewsets 模块
from .viewsets import BaseModelViewSet

# 导出 serializers 模块
from .serializers import (
    BaseModelSerializer,
    DynamicFieldsModelSerializer,
    NestedModelSerializer
)

# 导出 permissions 模块
from .permissions import (
    IsSuperUserOrReadOnly,
    IsOwnerOrReadOnly,
    IsStaffOrCreateOnly,
    IsActiveUser,
    IsSameUserOrReadOnly
)

# 导出 utils 模块
from .utils import (
    generate_random_string,
    generate_md5,
    get_client_ip,
    format_datetime,
    get_today,
    get_now,
    validate_positive,
    validate_min_length,
    validate_max_length,
    create_success_response,
    create_error_response,
    create_paginated_response
)

# 导出 mixins 模块
from .mixins import (
    ReadOnlyModelMixin,
    CreateUpdateModelMixin,
    CreateDestroyModelMixin,
    UpdateDestroyModelMixin,
    DestroyProtectedModelMixin,
    AuditModelMixin,
    LoggingModelMixin,
    BulkCreateModelMixin
)

__version__ = "0.1.0"
__all__ = [
    # pagination
    "DefaultPagination",
    
    # viewsets
    "BaseModelViewSet",
    
    # serializers
    "BaseModelSerializer",
    "DynamicFieldsModelSerializer",
    "NestedModelSerializer",
    
    # permissions
    "IsSuperUserOrReadOnly",
    "IsOwnerOrReadOnly",
    "IsStaffOrCreateOnly",
    "IsActiveUser",
    "IsSameUserOrReadOnly",
    
    # utils
    "generate_random_string",
    "generate_md5",
    "get_client_ip",
    "format_datetime",
    "get_today",
    "get_now",
    "validate_positive",
    "validate_min_length",
    "validate_max_length",
    "create_success_response",
    "create_error_response",
    "create_paginated_response",
    
    # mixins
    "ReadOnlyModelMixin",
    "CreateUpdateModelMixin",
    "CreateDestroyModelMixin",
    "UpdateDestroyModelMixin",
    "DestroyProtectedModelMixin",
    "AuditModelMixin",
    "LoggingModelMixin",
    "BulkCreateModelMixin"
]
