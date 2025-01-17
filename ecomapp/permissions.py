from rest_framework.permissions import BasePermission

class IsVendor(BasePermission):
    def has_permission(self, request, view):
        print("1 st",request.user.is_authenticated)
        print("2 nd",request.user.id)
        return True