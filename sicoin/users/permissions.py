from rest_framework import permissions


class CheckRole:
    def role_is_present(self, user, role):
        roles = list(user.groups.values_list('name', flat=True))
        return role in roles


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsResourceRole(permissions.BasePermission, CheckRole):
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return self.role_is_present(user=request.user, role=ValidRoles.RESOURCE.value)
