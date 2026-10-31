from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from clients.models import Client
from subscriptions.models import Subscription


@receiver([post_save, post_delete], sender=Client)
@receiver([post_save, post_delete], sender=Subscription)
def invalidate_dashboard_cache(sender, **kwargs):
    transaction.on_commit(
        lambda: cache.delete("dashboard_stats")
    )