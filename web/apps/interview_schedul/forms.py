from django import forms


class BookSlotForm(forms.Form):
    candidate_name = forms.CharField(
        label="Ваше имя",
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Иван Петров", "autocomplete": "name"}),
    )
    candidate_email = forms.EmailField(
        label="Ваш email",
        widget=forms.EmailInput(attrs={"placeholder": "ivan@example.com", "autocomplete": "email"}),
    )
    slot = forms.CharField(
        widget=forms.HiddenInput(),
    )

    def clean_slot(self):
        from datetime import datetime
        import pytz

        raw = self.cleaned_data.get("slot", "")
        tz = pytz.timezone("Europe/Moscow")
        try:
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
        except (ValueError, TypeError):
            raise forms.ValidationError("Некорректный формат даты/времени.")
        return dt