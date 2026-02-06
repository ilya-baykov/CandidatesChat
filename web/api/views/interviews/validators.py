from rest_framework.exceptions import ValidationError
import uuid


class Validator:
    @staticmethod
    def validate_uuid(token: str | None) -> uuid.UUID:
        if not token:
            raise ValidationError({"token": "Параметр token обязателен"})
        try:
            return uuid.UUID(token)
        except ValueError:
            raise ValidationError({"token": "Некорректный формат UUID"})

    @staticmethod
    def validate_candidate_vacancy_params(candidate_id: str | None, vacancy_id: str | None) -> tuple[int, int]:
        if not candidate_id or not vacancy_id:
            raise ValidationError({"detail": "Требуются параметры candidate_id и vacancy_id"})
        try:
            return int(candidate_id), int(vacancy_id)
        except (ValueError, TypeError):
            raise ValidationError({"detail": "candidate_id и vacancy_id должны быть целыми числами"})
