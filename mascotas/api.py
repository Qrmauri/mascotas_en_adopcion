from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Mascota
from .permissions import EsAutorOSoloLectura
from .serializers import MascotaSerializer


class MascotaViewSet(viewsets.ModelViewSet):
    """AE 3.1.4: CRUD completo + endpoint /mios/."""

    queryset = Mascota.objects.select_related("autor")
    serializer_class = MascotaSerializer
    # Leer: cualquiera. Escribir: autenticado (401 sin token) y además autor del objeto (403)
    permission_classes = [IsAuthenticatedOrReadOnly, EsAutorOSoloLectura]

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def mios(self, request):
        qs = self.get_queryset().filter(autor=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(qs, many=True).data)
