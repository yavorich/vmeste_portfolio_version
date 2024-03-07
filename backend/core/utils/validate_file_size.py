from rest_framework.exceptions import ValidationError


def validate_file_size(file):
    """Установить ограничение для загружаемых файлов"""
    if not file:
        return
    max_size = 200 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError({"error": "Размер файла не должен превышать 50 МБ."})
