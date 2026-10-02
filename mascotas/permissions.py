from rest_framework import permissions


class EsAutorOSoloLectura(permissions.BasePermission):
    """AE 3.1.2: lectura para todos; modificar/borrar solo el autor (si no, 403)."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.autor == request.user
