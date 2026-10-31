from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from clients.models import Client
from subscriptions.models import Subscription


class DashboardAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = cache.get("dashboard_stats")

        if data is None:
            data = {
                "clients_count": Client.objects.count(),
                "active_subscriptions": Subscription.objects.filter(
                    is_active=True
                ).count(),
            }

            cache.set("dashboard_stats", data, timeout=60)

        return Response(data)