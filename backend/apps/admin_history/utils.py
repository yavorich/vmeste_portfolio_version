from django.core.exceptions import FieldDoesNotExist


def get_model_field_label(model, field):
    try:
        return str(model._meta.get_field(field).verbose_name)
    except FieldDoesNotExist:
        return str(field)
