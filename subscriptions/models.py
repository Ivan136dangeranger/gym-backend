from django.db import models


class Subscription(models.Model):
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.DO_NOTHING,
        db_column="client_id",
        related_name="subscriptions"
    )

    total_sessions = models.IntegerField()

    remaining_sessions = models.IntegerField()

    purchase_date = models.DateField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Subscription #{self.pk}"

    class Meta:
        db_table = "subscriptions"
        unique_together = (("id", "client"),)
