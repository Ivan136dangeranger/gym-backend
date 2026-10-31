from django.db import transaction
from django.db.models import F

from .models import Subscription


@transaction.atomic
def use_subscription_session(subscription_id):
    subscription = Subscription.objects.select_for_update().get(
        id=subscription_id
    )

    if not subscription.is_active:
        raise ValueError("Абонемент неактивен")

    if subscription.remaining_sessions <= 0:
        raise ValueError("Занятия закончились")

    subscription.remaining_sessions = F("remaining_sessions") - 1
    subscription.save(update_fields=["remaining_sessions"])

    subscription.refresh_from_db()

    return subscription