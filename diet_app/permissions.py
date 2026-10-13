from rest_framework.permissions import BasePermission
from diet_app.models import CustomUser

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj,CustomUser):
            return request.user==obj
        return request.user==obj.owner