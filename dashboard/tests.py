import pytest

from django.core.cache import cache
from django.test import override_settings
from clients.models import Client


@pytest.mark.django_db(transaction=True)
def test_dashboard_cache_invalidation():
    cache.set(
        "dashboard_stats",
        {"clients_count": 999},
        timeout=300,
    )

    assert cache.get("dashboard_stats") is not None

    Client.objects.create(
        name="Cache Test Client",
        email="cache.test@example.com",
    )

    assert cache.get("dashboard_stats") is None