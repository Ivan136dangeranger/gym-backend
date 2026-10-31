from celery import shared_task
from time import sleep


@shared_task
def send_subscription_email(email):
    sleep(3)
    return f"Email sent to {email}"

