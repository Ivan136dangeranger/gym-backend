import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from psycopg.errors import UniqueViolation

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def get_client_by_id(client_id):
    with get_connection() as conn:

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, name, email FROM clients WHERE id = %s;", (client_id,)
            )

            client = cur.fetchone()

            return client


result = get_client_by_id(2)

print(result)


def get_all_clients():
    with get_connection() as conn:

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT id, name, email FROM clients ORDER BY id;")

            clients = cur.fetchall()

            return clients


clients = get_all_clients()

for client in clients:
    print(client["name"])


def create_client(name, email):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO clients (name, email)
                VALUES (%s, %s)
                RETURNING id, name, email;
                """,
                (name, email),
            )

            client = cur.fetchone()
            return client


try:
    new_client = create_client("John Smith", "john.smith@example.com")
    print("Клиент создан:", new_client)

except UniqueViolation:
    print("Ошибка: клиент с таким email уже существует")
