# 最小 Django 配置测试
import os
import django
from django.conf import settings

# 设置最小 Django 配置
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'rest_framework',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
    )
    django.setup()

# 现在测试 drf-base 包的导入功能
print("Testing drf-base package imports with Django configured...")

# 测试版本导入
try:
    from drf_base import __version__
    print(f"✓ Version: {__version__}")
except Exception as e:
    print(f"✗ Failed to import version: {e}")

# 测试 pagination 导入
try:
    from drf_base import DefaultPagination
    print(f"✓ DefaultPagination imported successfully")
except Exception as e:
    print(f"✗ Failed to import DefaultPagination: {e}")

# 测试 viewsets 导入
try:
    from drf_base import BaseModelViewSet
    print(f"✓ BaseModelViewSet imported successfully")
except Exception as e:
    print(f"✗ Failed to import BaseModelViewSet: {e}")

# 测试 serializers 导入
try:
    from drf_base import (
        BaseModelSerializer,
        DynamicFieldsModelSerializer,
        NestedModelSerializer
    )
    print(f"✓ Serializers imported successfully")
except Exception as e:
    print(f"✗ Failed to import serializers: {e}")

# 测试 permissions 导入
try:
    from drf_base import (
        IsSuperUserOrReadOnly,
        IsOwnerOrReadOnly,
        IsStaffOrCreateOnly,
        IsActiveUser,
        IsSameUserOrReadOnly
    )
    print(f"✓ Permissions imported successfully")
except Exception as e:
    print(f"✗ Failed to import permissions: {e}")

# 测试 utils 导入
try:
    from drf_base import (
        generate_random_string,
        generate_md5,
        format_datetime
    )
    print(f"✓ Utils imported successfully")
    # 测试简单的工具函数
    print(f"  - Random string: {generate_random_string(8)}")
    print(f"  - MD5 of 'test': {generate_md5('test')}")
except Exception as e:
    print(f"✗ Failed to import utils: {e}")

# 测试 mixins 导入
try:
    from drf_base import (
        ReadOnlyModelMixin,
        CreateUpdateModelMixin,
        AuditModelMixin,
        BulkCreateModelMixin
    )
    print(f"✓ Mixins imported successfully")
except Exception as e:
    print(f"✗ Failed to import mixins: {e}")

print("\nAll import tests completed!")
