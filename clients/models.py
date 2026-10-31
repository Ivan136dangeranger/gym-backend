from django.db import models
from django.utils import timezone


class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    registration_date = models.DateField(
        default=timezone.localdate,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True,
        blank=True,
        null=True
    )

    trainer = models.ForeignKey(
        "trainers.Trainer",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="trainer_id",
        related_name="clients"
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "clients"