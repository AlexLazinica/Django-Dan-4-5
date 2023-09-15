from rest_framework.permissions import BasePermission


class IsTaskOwnerOrAdmin(BasePermission):
    """
    Allow only creators of task and admin users to manipulate it
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or obj.user == request.user:
            return True
        return False