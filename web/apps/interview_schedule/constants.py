from datetime import time

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


EMAIL_SUBJECT = "Приглашение в календаре"
EMAIL_BODY_TEMPLATE = (
    "Вы получили приглашение на встречу.\n\n"
    "Тема: {summary}\n"
    "Время: {start:%d.%m.%Y %H:%M} МСК\n"
    "Место: {location}\n\n"
    "Если приглашение не добавилось автоматически — "
    "откройте вложение invite.ics вручную."
)

SLOT_DURATION_MINUTES = 60
WORK_START = time(10, 0)
WORK_END = time(18, 0)
WORK_DAYS = frozenset({0, 1, 2, 3, 4})  # Пн–Пт

EMAIL_ACCEPT_BODY_TEMPLATE = (
    "Привет, {candidate_name}!\n\n"
    "Ваше интервью подтверждено:\n\n"
    "  📅 Дата:   {local_start:%d.%m.%Y}\n"
    "  🕐 Время:  {local_start:%H:%M} – {local_end:%H:%M} МСК\n"
    "  📍 Место:  {location}\n\n"
    "Если возникнут вопросы — напишите рекрутеру: {recruiter_email}\n\n"
    "Удачи! 🚀"
)
