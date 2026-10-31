import pytest

from concurrent.futures import ThreadPoolExecutor
from django.db import close_old_connections

from subscriptions.services import use_subscription_session

@pytest.mark.django_db(transaction=True)
def test_concurrent_subscription_use(test_subscription):
    # Оставляем клиенту одно занятие
    test_subscription.remaining_sessions = 1
    test_subscription.save(update_fields=["remaining_sessions"])

    subscription_id = test_subscription.id

    def use_session():
        close_old_connections()
        try:
            use_subscription_session(subscription_id)
            return "success"
        except ValueError:
            return "rejected"
        finally:
            close_old_connections()

    # Два потока пытаются списать одно занятие
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: use_session(), range(2)))

    # Одно списание успешно, второе отклонено
    assert results.count("success") == 1
    assert results.count("rejected") == 1

    test_subscription.refresh_from_db()
    assert test_subscription.remaining_sessions == 0