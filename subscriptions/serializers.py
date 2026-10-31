from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = [
            "id",
            "client",
            "total_sessions",
            "remaining_sessions",
            "purchase_date",
            "is_active"
        ]

    def validate(self, attrs):
        total = attrs.get(
            "total_sessions",
            self.instance.total_sessions if self.instance else None
        )

        remaining = attrs.get(
            "remaining_sessions",
            self.instance.remaining_sessions if self.instance else None
        )

        if total is None or remaining is None:
            raise serializers.ValidationError(
                "Необходимо указать количество занятий."
            )

        if total <= 0:
            raise serializers.ValidationError(
                "Общее количество занятий должно быть больше нуля."
            )

        if remaining < 0 or remaining > total:
            raise serializers.ValidationError(
                "Оставшееся количество занятий должно быть от 0 до общего количества."
            )

        return attrs