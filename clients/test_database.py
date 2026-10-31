import pytest
from django.db import connection


@pytest.mark.django_db
def test_database_connection():
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database();")
        database_name = cursor.fetchone()[0]

    print(f"\nConnected database: {database_name}")

    assert database_name.startswith("test_")