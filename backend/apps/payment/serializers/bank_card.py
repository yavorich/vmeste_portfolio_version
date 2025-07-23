from rest_framework.serializers import (
    Serializer,
    IntegerField,
    CharField,
    SerializerMethodField,
)


class BankCardSerializer(Serializer):
    id = IntegerField()
    pan = CharField()
    exp_date = SerializerMethodField()

    @staticmethod
    def get_exp_date(obj):
        exp_code = str(obj["exp_code"])
        return f"{exp_code[:2]}/{exp_code[2:]}"
