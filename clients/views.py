from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView

from .models import Client
from .serializers import ClientSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class ClientListAPIView(ListCreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Client.objects.all().order_by("id")

        return Client.objects.filter(
            trainer__user=user
        ).order_by("id")

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied(
                "Только администратор может создавать клиентов."
            )

        serializer.save()


class ClientDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Client.objects.all()

        return Client.objects.filter(trainer__user=user)

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied(
                "Только администратор может изменять клиентов."
            )

        serializer.save()