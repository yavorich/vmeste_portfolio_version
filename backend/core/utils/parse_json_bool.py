import json
from rest_framework.exceptions import ValidationError


def parse_json_bool(value):
    if value is not None:
        parsed_value = json.loads(value)
        if not isinstance(parsed_value, bool):
            raise ValidationError(f"Параметр {filter} должен иметь значение true/false")
        return parsed_value
    return None
