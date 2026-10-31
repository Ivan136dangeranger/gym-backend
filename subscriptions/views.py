
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription
from .serializers import SubscriptionSerializer
from .services import use_subscription_session
from django.db import transaction
from .tasks import send_subscription_email


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return request.user.is_staff


class SubscriptionPagination(PageNumberPagination):
    page_size = 2


def available_subscriptions(user):
    if user.is_staff:
        return Subscription.objects.all().order_by("id")

    return Subscription.objects.filter(
        client__trainer__user=user
    ).order_by("id")


class SubscriptionListAPIView(ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["client", "is_active"]
    pagination_class = SubscriptionPagination

    def get_queryset(self):
        return available_subscriptions(self.request.user)

    def perform_create(self, serializer):
        subscription = serializer.save()

        email = subscription.client.email

        if email:
            transaction.on_commit(
                lambda: send_subscription_email.delay(email)
            )


class SubscriptionDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return available_subscriptions(self.request.user)


class SubscriptionUseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Сначала проверяем, имеет ли пользователь доступ
        # к абонементу. Чужие абонементы недоступны.
        if not available_subscriptions(request.user).filter(pk=pk).exists():
            raise Http404

        try:
            subscription = use_subscription_session(pk)

        except Subscription.DoesNotExist:
            raise Http404

        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SubscriptionSerializer(subscription)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
