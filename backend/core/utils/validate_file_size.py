from rest_framework.exceptions import ValidationError


def validate_file_size(file, max_size_mb):
    """Установить ограничение для загружаемых файлов"""
    if not file:
        return
    max_size = max_size_mb * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(
            {"error": f"Размер файла не должен превышать {max_size_mb} МБ."}
        )
