from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


class ReadOnlyModelMixin(mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """只读模型混合类，组合了 List 和 Retrieve 功能"""
    pass


class CreateUpdateModelMixin(mixins.CreateModelMixin, mixins.UpdateModelMixin):
    """创建更新模型混合类，组合了 Create 和 Update 功能"""
    pass


class CreateDestroyModelMixin(mixins.CreateModelMixin, mixins.DestroyModelMixin):
    """创建删除模型混合类，组合了 Create 和 Destroy 功能"""
    pass


class UpdateDestroyModelMixin(mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """更新删除模型混合类，组合了 Update 和 Destroy 功能"""
    pass


class DestroyProtectedModelMixin(mixins.DestroyModelMixin):
    """删除保护模型混合类，防止删除被引用的对象"""
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'detail': f'无法删除对象：{str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AuditModelMixin:
    """审计模型混合类，自动记录创建者和更新者"""
    
    def perform_create(self, serializer):
        # 自动设置创建者和创建时间
        serializer.save(
            created_by=self.request.user,
            created_at=timezone.now()
        )
    
    def perform_update(self, serializer):
        # 自动设置更新者和更新时间
        serializer.save(
            updated_by=self.request.user,
            updated_at=timezone.now()
        )


class LoggingModelMixin:
    """日志模型混合类，记录请求日志"""
    
    def perform_create(self, serializer):
        # 可以在这里添加创建日志
        instance = serializer.save()
        # 示例：print(f'Created {instance.__class__.__name__} with id {instance.id}')
        return instance
    
    def perform_update(self, serializer):
        # 可以在这里添加更新日志
        instance = serializer.save()
        # 示例：print(f'Updated {instance.__class__.__name__} with id {instance.id}')
        return instance
    
    def perform_destroy(self, instance):
        # 可以在这里添加删除日志
        # 示例：print(f'Deleted {instance.__class__.__name__} with id {instance.id}')
        instance.delete()


class BulkCreateModelMixin:
    """批量创建模型混合类，支持一次性创建多个对象"""
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super().create(request, *args, **kwargs)
    
    def perform_bulk_create(self, serializer):
        serializer.save()
