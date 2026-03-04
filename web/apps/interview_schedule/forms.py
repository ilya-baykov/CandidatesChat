import pytz
from datetime import datetime
from django import forms


class BookSlotForm(forms.Form):
    candidate_email = forms.EmailField(
        label="Ваш email",
        widget=forms.EmailInput(attrs={"placeholder": "ivan@example.com", "autocomplete": "email"}),
    )
    comment = forms.CharField(
        label="Комментарий",
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Необязательно"}),
    )
    slot = forms.CharField(
        widget=forms.HiddenInput(),
    )

    def clean_slot(self):

        raw = self.cleaned_data.get("slot", "")
        tz = pytz.timezone("Europe/Moscow")
        try:
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
        except (ValueError, TypeError):
            raise forms.ValidationError("Некорректный формат даты/времени.")
        return dt
