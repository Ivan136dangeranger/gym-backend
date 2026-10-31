from django.conf import settings
from django.db import models


class Trainer(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.IntegerField(blank=True, null=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trainer_profile",
    )

    def __str__(self):
        return self.name or f"Trainer #{self.pk}"

    class Meta:
        db_table = "trainers"