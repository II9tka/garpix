"""
    Permissions
"""

from rest_framework.permissions import SAFE_METHODS, IsAuthenticated


class IsOwnerOrReadOnlyIfAuthenticated(IsAuthenticated):
    """
        IsOwnerOrReadOnly permission.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user == obj.creator
