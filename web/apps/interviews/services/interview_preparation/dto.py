from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateContextDTO:
    id: int
    resume_text: str


@dataclass(frozen=True)
class VacancyContextDTO:
    id: int
    title: str
    city: str
    job_title: str
    main_responsibilities: str
    required_experience: str
    software_knowledge: str
    wishes_prompt: str

    @property
    def prompt_description(self) -> str:
        """Человекочитаемое описание вакансии для промпта"""
        fields = [
            ("Название вакансии", self.job_title or self.title),
            ("Регион", self.city),
            ("Основные обязанности", self.main_responsibilities),
            ("Требуемый опыт работы", self.required_experience),
            ("Необходимые знания и технологии", self.software_knowledge),
            ("Дополнительные пожелания", self.wishes_prompt),
        ]

        lines = []
        for label, value in fields:
            if value:  # игнорируем None / "" / пустую строку
                lines.append(f"{label}:\n{value.strip()}")

        return "\n\n".join(lines)
