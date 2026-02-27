from rest_framework import serializers

from apps.interviews.models import Interview


class QuestionInputSerializer(serializers.Serializer):
    order = serializers.IntegerField(min_value=1)
    text = serializers.CharField(min_length=1, max_length=2000)


class InterviewCreateInputSerializer(serializers.Serializer):
    """
    Входной сериализатор для эндпоинта создания/поиска интервью (POST /interviews/).
    При невалидных данных будет возвращена 400 Bad Request с детальным описанием ошибок.
    """
    candidate_id = serializers.IntegerField(help_text="ID кандидата из системы ОКО")
    vacancy_id = serializers.IntegerField(help_text="ID вакансии из системы ОКО")
    questions = QuestionInputSerializer(many=True, required=False, default=None)

    def validate_questions(self, value):  # noqa
        if value and len(value) > 10:
            raise serializers.ValidationError("Нельзя передать более 10 вопросов.")
        return value


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
        read_only_fields = ['id', 'token', 'status', 'started_at', 'completed_at', 'total_score']


class FrontInterviewSummarySerializer(serializers.Serializer):
    """Сериализатор для сводки интервью в формате фронтенда."""
    candidate_id = serializers.IntegerField()
    vacancy_id = serializers.IntegerField()
    current_status = serializers.CharField()
    first_message_date = serializers.CharField(allow_null=True)
    last_message_date = serializers.CharField(allow_null=True)
    total_score = serializers.FloatField(allow_null=True)
    started_at = serializers.CharField(allow_null=True)
    completed_at = serializers.CharField(allow_null=True)
    is_completed = serializers.BooleanField()
    is_in_progress = serializers.BooleanField()
    dialogue_history = serializers.ListField(child=serializers.DictField())
