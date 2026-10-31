import pytest

from trainers.models import Trainer
from clients.models import Client
from subscriptions.models import Subscription
from django.apps import apps
from django.db import connection
from rest_framework.test import APIClient


@pytest.fixture(scope="session", autouse=True)
def create_test_tables(django_db_setup, django_db_blocker):

    with django_db_blocker.unblock():

        existing_tables = connection.introspection.table_names()

        trainer_model = apps.get_model("trainers", "Trainer")
        client_model = apps.get_model("clients", "Client")
        subscription_model = apps.get_model("subscriptions", "Subscription")

        with connection.schema_editor() as schema_editor:

            if trainer_model._meta.db_table not in existing_tables:
                schema_editor.create_model(trainer_model)

            if client_model._meta.db_table not in existing_tables:
                schema_editor.create_model(client_model)

            if subscription_model._meta.db_table not in existing_tables:
                schema_editor.create_model(subscription_model)


@pytest.fixture
def api_client(db):
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient

    User = get_user_model()

    user = User.objects.create_superuser(
        username="test_admin",
        email="test_admin@example.com",
        password="TestPassword123!"
    )

    client = APIClient()
    client.force_authenticate(user=user)

    return client


@pytest.fixture
def test_client(db):
    return Client.objects.create(
        name="Test Client",
        email="test.client@example.com"
    )

@pytest.fixture
def test_trainer(db):
    return Trainer.objects.create(
        name="John Smith",
        email="john.trainer@example.com",
        specialization="Strength Training",
        experience_years=5
    )

@pytest.fixture
def test_subscription(db, test_client):
    return Subscription.objects.create(
        client=test_client,
        total_sessions=10,
        remaining_sessions=7,
        is_active=True
    )