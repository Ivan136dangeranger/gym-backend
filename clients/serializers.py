from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "registration_date",
            "is_active",
            "trainer",
        ]

    # Проверка имени клиента
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Имя клиента должно содержать минимум 2 символа."
            )

        return value

    # Проверка взаимосвязи нескольких полей
    def validate(self, attrs):

        # Получаем итоговый статус клиента
        is_active = attrs.get(
            "is_active",
            self.instance.is_active if self.instance else True
        )

        # Получаем итогового тренера клиента
        trainer = attrs.get(
            "trainer",
            self.instance.trainer if self.instance else None
        )

        # Проверяем бизнес-правило
        if is_active is False and trainer is not None:
            raise serializers.ValidationError(
                "Неактивному клиенту нельзя назначать тренера."
            )

        return attrs