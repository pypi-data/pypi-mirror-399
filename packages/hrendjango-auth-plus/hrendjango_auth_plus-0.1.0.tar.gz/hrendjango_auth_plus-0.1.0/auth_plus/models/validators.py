from datetime import date
from django.core.exceptions import ValidationError

__all__ = ['validate_birth_date', 'validate_image_size']


def validate_birth_date(value):
    if value > date.today():
        raise ValidationError("Дата рождения не может быть в будущем.")


def validate_image_size(image):
    """Проверяет, что размер файла не превышает 2 МБ (можно изменить)."""
    max_size = 2 * 1024 * 1024  # 2 МБ в байтах
    if image.size > max_size:
        raise ValidationError(f"Максимальный размер файла — {max_size // (1024 * 1024)} МБ.")
