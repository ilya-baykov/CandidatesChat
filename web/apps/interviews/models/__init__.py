"""
Основные модели приложения interviews.

Логика:
- Candidate: снимок кандидата, используется для поиска и связи с внешними данными
- Vacancy: снимок вакансии из внешней системы
- Interview: корневая сущность, управляет flow диалога и статусом
- InterviewQuestion: вопрос в контексте интервью, упорядоченный
- InterviewAnswer: ответ на вопрос, один к одному с вопросом
- InterviewMessage: лог сообщений в рамках интервью
"""

# from .candidate import Candidate
# from .vacancy import Vacancy
from .interview import Interview
from .question import InterviewQuestion
from .answer import InterviewAnswer
from .interview_message import InterviewMessage
