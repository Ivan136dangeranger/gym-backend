import pytest

from clients.models import Client


@pytest.mark.django_db
def test_get_clients(api_client, test_client):

    response = api_client.get("/api/clients/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == test_client.name


@pytest.mark.django_db
def test_create_client(api_client):

    data = {
        "name": "John Wilson",
        "email": "john.wilson@example.com"
    }

    response = api_client.post(
        "/api/clients/",
        data,
        format="json"
    )

    assert response.status_code == 201
    assert response.data["name"] == "John Wilson"

    client = Client.objects.get(
        email="john.wilson@example.com"
    )

    assert client.name == "John Wilson"
    assert client.email == "john.wilson@example.com"
    assert client.id == response.data["id"]


@pytest.mark.django_db
def test_update_client_invalid_name(api_client):

    client = Client.objects.create(
        name="Robert Wilson",
        email="robert.test@example.com"
    )

    response = api_client.patch(
        f"/api/clients/{client.id}/",
        {"name": "A"},
        format="json"
    )

    assert response.status_code == 400
    assert "name" in response.data

    client.refresh_from_db()

    assert client.name == "Robert Wilson"


def test_get_client_detail(api_client, test_client):
    response = api_client.get(
        f"/api/clients/{test_client.id}/"
    )

    assert response.status_code == 200
    assert response.data["id"] == test_client.id
    assert response.data["name"] == test_client.name


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_name",
    [
        pytest.param("A", id="too-short"),
        pytest.param("", id="empty"),
        pytest.param("   ", id="spaces-only"),
    ]
)
def test_invalid_client_names(api_client, test_client, invalid_name):

    response = api_client.patch(
        f"/api/clients/{test_client.id}/",
        {"name": invalid_name},
        format="json"
    )

    assert response.status_code == 400
    assert "name" in response.data

    test_client.refresh_from_db()
    assert test_client.name == "Test Client"


def test_update_client_success(api_client, test_client):

    response = api_client.patch(
        f"/api/clients/{test_client.id}/",
        {
            "name": "Alexander Smith",
            "phone": "+905551234567"
        },
        format="json"
    )

    assert response.status_code == 200

    assert response.data["name"] == "Alexander Smith"
    assert response.data["phone"] == "+905551234567"

    test_client.refresh_from_db()

    assert test_client.name == "Alexander Smith"
    assert test_client.phone == "+905551234567"

    assert test_client.email == "test.client@example.com"


def test_assign_trainer_to_inactive_client(
    api_client,
    test_client,
    test_trainer
):
    # 1. Делаем клиента неактивным
    test_client.is_active = False
    test_client.save()

    # 2. Пытаемся назначить тренера
    response = api_client.patch(
        f"/api/clients/{test_client.id}/",
        {"trainer": test_trainer.id},
        format="json"
    )

    # 3. Проверяем отказ API
    assert response.status_code == 400

    # 4. Проверяем, что тренер не назначен
    test_client.refresh_from_db()

    assert test_client.trainer_id is None


def test_assign_trainer_to_active_client(
    api_client,
    test_client,
    test_trainer
):
    # Убеждаемся, что клиент активен
    test_client.is_active = True
    test_client.save()

    # Назначаем тренера через PATCH
    response = api_client.patch(
        f"/api/clients/{test_client.id}/",
        {"trainer": test_trainer.id},
        format="json"
    )

    # Проверяем успешный ответ
    assert response.status_code == 200

    # Проверяем, что API вернул ID тренера
    assert response.data["trainer"] == test_trainer.id

    # Проверяем данные в PostgreSQL
    test_client.refresh_from_db()

    assert test_client.trainer_id == test_trainer.id