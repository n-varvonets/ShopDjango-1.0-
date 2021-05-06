from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):  # http://i.imgur.com/RIjsqmC.png
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  #  проверяет является метод этого запроса безопасным(get,head.options)
            return True
        return obj.user == request.user

