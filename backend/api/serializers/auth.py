from rest_framework import serializers

from api.models import User
from api.services import generate_confirmation_code


class PhoneAuthSendCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    confirmation_code = serializers.SerializerMethodField()

    def get_confirmation_code(self, obj):
        return "11111"
        # return generate_confirmation_code()


class EmailAuthSendCodeSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["email", "confirmation_code"]

    def validate_email(self, value):
        if self.context["user"].email != value:
            raise serializers.ValidationError("Неправильная почта")
        return value

    def get_confirmation_code(self, obj):
        return generate_confirmation_code()


class PhoneAuthSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    confirmation_code = serializers.CharField(max_length=5)

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Неверный номер телефона")
        return value


class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=5)

    def validate_email(self, value):
        if self.context["user"].email != value:
            raise serializers.ValidationError("Неправильная почта")
        return value
