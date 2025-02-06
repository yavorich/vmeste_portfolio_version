from django.core.exceptions import FieldDoesNotExist


def get_model_field_label(model, field):
    try:
        return str(model._meta.get_field(field).verbose_name)
    except FieldDoesNotExist:
        return str(field)


def get_object_data_from_obj(obj):
    history_fields = (
        obj._meta.history_fields if hasattr(obj._meta, "history_fields") else {}
    )
    return {field: str(getattr(obj, field)) for field in history_fields}
