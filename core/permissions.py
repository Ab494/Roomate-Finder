# This file defines custom permission classes for the Roommate Finder API.
# Permissions control who can access specific views and perform certain actions.

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission that allows read access to anyone, but write access only to object owners.

    This is commonly used for user-generated content where users can view everything
    but only edit their own items.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions (GET, HEAD, OPTIONS) are allowed to any request
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        # Assumes the object has an 'owner' field
        return obj.owner == request.user


class IsAdminUser(BasePermission):
    """
    Custom permission that only allows access to admin/staff users.

    This is used for administrative endpoints like user moderation,
    system statistics, and platform management.
    """

    def has_permission(self, request, view):
        # Check if user exists and has staff/admin privileges
        return request.user and request.user.is_staff


class IsVerified(BasePermission):
    """Only verified users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_verified


class IsOwner(BasePermission):
    """
    Only allows access to the owner of the object.
    No read access for non-owners (stricter than IsOwnerOrReadOnly).
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
