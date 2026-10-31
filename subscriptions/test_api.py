from rest_framework import status

from subscriptions.models import Subscription
from subscriptions.services import use_subscription_session
import pytest
from rest_framework.test import APIClient
from django.db import transaction
from unittest.mock import patch


# 1. Получение списка абонементов с пагинацией
def test_get_subscriptions(api_client, test_subscription):
    response = api_client.get("/api/subscriptions/")

    assert response.status_code == status.HTTP_200_OK

    data = response.data

    assert data["count"] == 1
    assert len(data["results"]) == 1

    subscription = data["results"][0]

    assert subscription["id"] == test_subscription.id
    assert subscription["client"] == test_subscription.client_id
    assert subscription["total_sessions"] == 10
    assert subscription["remaining_sessions"] == 7
    assert subscription["is_active"] is True


# 2. Нельзя создать абонемент с некорректным количеством занятий
def test_create_subscription_invalid_sessions(api_client, test_client):
    data = {
        "client": test_client.id,
        "total_sessions": 5,
        "remaining_sessions": 10,
        "is_active": True,
    }

    response = api_client.post(
        "/api/subscriptions/",
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# 3. Успешное создание абонемента
def test_create_subscription_success(api_client, test_client):
    data = {
        "client": test_client.id,
        "total_sessions": 10,
        "remaining_sessions": 10,
        "is_active": True,
    }

    response = api_client.post(
        "/api/subscriptions/",
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["client"] == test_client.id
    assert response.data["total_sessions"] == 10
    assert response.data["remaining_sessions"] == 10

    assert Subscription.objects.filter(
        client=test_client
    ).exists()


# 4. Сервис не списывает занятие при нулевом остатке
def test_use_session_with_zero_balance(test_subscription):
    test_subscription.remaining_sessions = 0
    test_subscription.save(update_fields=["remaining_sessions"])

    with pytest.raises(ValueError):
        use_subscription_session(test_subscription.id)

    test_subscription.refresh_from_db()

    assert test_subscription.remaining_sessions == 0


# 5. Успешное списание занятия через API
def test_use_subscription_api(api_client, test_subscription):
    url = f"/api/subscriptions/{test_subscription.id}/use/"

    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["remaining_sessions"] == 6

    test_subscription.refresh_from_db()

    assert test_subscription.remaining_sessions == 6


# 6. API запрещает списание при нулевом остатке
def test_use_subscription_api_zero_balance(api_client, test_subscription):
    test_subscription.remaining_sessions = 0
    test_subscription.save(update_fields=["remaining_sessions"])

    url = f"/api/subscriptions/{test_subscription.id}/use/"

    response = api_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    test_subscription.refresh_from_db()

    assert test_subscription.remaining_sessions == 0


# 7. API запрещает списание неактивного абонемента
def test_use_subscription_api_inactive(api_client, test_subscription):
    test_subscription.is_active = False
    test_subscription.save(update_fields=["is_active"])

    url = f"/api/subscriptions/{test_subscription.id}/use/"

    response = api_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    test_subscription.refresh_from_db()

    assert test_subscription.remaining_sessions == 7


# 8. Списание несуществующего абонемента
def test_use_subscription_api_not_found(api_client, db):
    response = api_client.post(
        "/api/subscriptions/999999/use/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# 9. Получение конкретного абонемента
def test_get_subscription_detail(api_client, test_subscription):
    url = f"/api/subscriptions/{test_subscription.id}/"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == test_subscription.id
    assert response.data["client"] == test_subscription.client_id
    assert response.data["remaining_sessions"] == 7


# 10. Получение несуществующего абонемента
def test_get_subscription_detail_not_found(api_client, db):
    response = api_client.get(
        "/api/subscriptions/999999/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# 11. Изменение статуса абонемента
def test_update_subscription_status(api_client, test_subscription):
    url = f"/api/subscriptions/{test_subscription.id}/"

    response = api_client.patch(
        url,
        {"is_active": False},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    test_subscription.refresh_from_db()

    assert test_subscription.is_active is False


# 12. Запрет некорректного количества занятий при изменении
def test_update_subscription_invalid_sessions(api_client, test_subscription):
    url = f"/api/subscriptions/{test_subscription.id}/"

    response = api_client.patch(
        url,
        {"remaining_sessions": 20},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    test_subscription.refresh_from_db()

    assert test_subscription.remaining_sessions == 7


# 13. Успешное списание непосредственно через сервис
def test_use_subscription_session(test_subscription):
    subscription = use_subscription_session(
        test_subscription.id
    )

    assert subscription.remaining_sessions == 6

    test_subscription.refresh_from_db()

    assert test_subscription.remaining_sessions == 6


@pytest.mark.django_db(transaction=True)
def test_subscription_sends_email(admin_user, test_client):
    api = APIClient()
    api.force_authenticate(user=admin_user)

    with patch("subscriptions.views.send_subscription_email.delay") as mock_delay:
        response = api.post(
            "/api/subscriptions/",
            {
                "client": test_client.id,
                "total_sessions": 10,
                "remaining_sessions": 10,
                "is_active": True,
            },
            format="json",
        )

        assert response.status_code == 201
        mock_delay.assert_called_once_with(test_client.email)


@pytest.mark.django_db(transaction=True)
def test_email_not_sent_after_rollback(test_client):

    with patch("subscriptions.views.send_subscription_email.delay") as mock_delay:

        try:
            with transaction.atomic():
                transaction.on_commit(
                    lambda: mock_delay(test_client.email)
                )

                raise ValueError("Transaction failed")

        except ValueError:
            pass

        mock_delay.assert_not_called()