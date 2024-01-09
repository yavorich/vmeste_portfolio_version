import os


def delete_file(instance, file_field_name):
    file_field = getattr(instance, file_field_name)
    if file_field:
        file_path = file_field.path
        try:
            file_field.delete(save=False)
            file_directory = os.path.dirname(file_path)
            if not os.listdir(file_directory):
                os.rmdir(file_directory)
        except ValueError:
            print("невозможно удалить объект")
        except FileNotFoundError:
            print("директория или файл не найдены")


def delete_file_on_update(sender, instance, file_field_name, **kwargs):
    file_field = getattr(instance, file_field_name)
    file_name = str(file_field).split("/")[-1]
    if instance._state.adding or not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        old_file_field = getattr(old_instance, file_field_name)
        old_file_name = str(old_file_field).split("/")[-1]
    except sender.DoesNotExist:
        return

    if old_file_name != file_name:
        old_file_field.delete(save=False)
