from rest_framework import serializers
from rest_framework.fields import empty


class BaseModelSerializer(serializers.ModelSerializer):
    """基础 ModelSerializer，提供常用配置"""
    
    class Meta:
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """支持动态字段的序列化器
    
    用法：
    serializer = UserSerializer(user, fields=['id', 'username'])
    """
    
    def __init__(self, instance=None, data=empty, **kwargs):
        # 提取 fields 参数
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        
        super().__init__(instance, data, **kwargs)
        
        # 动态过滤字段
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude is not None:
            for field_name in exclude:
                if field_name in self.fields:
                    self.fields.pop(field_name)


class NestedModelSerializer(BaseModelSerializer):
    """支持嵌套序列化的基础序列化器
    
    用法：
    class Meta:
        model = User
        fields = ['id', 'username', 'profile']
        nested_fields = {
            'profile': ProfileSerializer(fields=['bio', 'avatar'])
        }
    """
    
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        
        # 处理嵌套字段
        nested_fields = getattr(self.Meta, 'nested_fields', {})
        for field_name, serializer in nested_fields.items():
            if field_name in self.fields:
                self.fields[field_name] = serializer
