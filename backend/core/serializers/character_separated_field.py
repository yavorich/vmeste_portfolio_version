from rest_framework.serializers import ListField


class CharacterSeparatedField(ListField):
    def __init__(self, *args, **kwargs):
        self.separator = kwargs.pop("separator", ",")
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        try:
            data = data.split(self.separator)
        except AttributeError:
            data = data[0].split(self.separator)
        return super().to_internal_value(data)
