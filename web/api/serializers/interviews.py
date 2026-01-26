from rest_framework import serializers

from apps.interviews.models import Interview


class InterviewCreateInputSerializer(serializers.Serializer):
    """
    Входной сериализатор для эндпоинта создания/поиска интервью (POST /interviews/).
    При невалидных данных будет возвращена 400 Bad Request с детальным описанием ошибок.
    """

    candidate_id = serializers.UUIDField(help_text="UUID кандидата из системы ОКО")
    vacancy_id = serializers.UUIDField(help_text="UUID вакансии из системы ОКО")


class InterviewDetailSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для представления объекта Interview.

    Используется для:
    - ответа на создание/поиск интервью (POST /interviews/)
    - получения интервью по токену (GET /interviews/by-token/)
    - получения интервью по паре кандидат+вакансия (GET /interviews/by-candidate-vacancy/)

    """

    status = serializers.CharField(source='status.code', read_only=True,
                                   help_text="Строковый код текущего статуса интервью")

    class Meta:
        model = Interview
        fields = [
            'id',
            'token',
            'status',
            'started_at',
            'completed_at',
            'total_score',
        ]
        read_only_fields = '__all__'
