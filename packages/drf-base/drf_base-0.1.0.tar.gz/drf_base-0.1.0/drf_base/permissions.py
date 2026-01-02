from rest_framework import permissions


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """超级用户可以写，普通用户只能读"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class IsOwnerOrReadOnly(permissions.BasePermission):
    """只有资源所有者可以修改，其他人只能读"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 检查 obj 是否有 owner 字段或 user 字段
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsStaffOrCreateOnly(permissions.BasePermission):
    """工作人员可以修改，普通用户只能创建"""
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and request.user.is_staff


class IsActiveUser(permissions.BasePermission):
    """只有活跃用户可以访问"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_active


class IsSameUserOrReadOnly(permissions.BasePermission):
    """只有用户自己可以修改自己的信息，其他人只能读"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
