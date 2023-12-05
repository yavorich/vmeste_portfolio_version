from rest_framework import serializers
from api.models import User
from api.services import generate_confirmation_code


class PhoneAuthSendCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_number", "confirmation_code"]

    def create(self, validated_data):
        phone_number = validated_data["phone_number"]
        # confirmation_code = generate_confirmation_code()
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            user = User.objects.create_user(
                phone_number=phone_number,
                confirmation_code="11111",
            )
        return user


class EmailAuthSendCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "confirmation_code"]

    def validate_email(self, value):
        if self.context["user"].email != value:
            raise serializers.ValidationError("Неправильная почта")
        return value

    def create(self, validated_data):
        user = self.context["user"]
        user.confirmation_code = generate_confirmation_code()
        user.save()
        return user


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
