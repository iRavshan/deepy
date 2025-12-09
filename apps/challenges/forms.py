from django import forms
from .models import Submission

class ChallangeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["code", "language"]

        widgets = {
            "code": forms.Textarea(attrs={
                "rows": 10,
                "placeholder": "Kodingizni shu yerga yozing...",
                "class": "form-control"
            }),
            "language": forms.Select(attrs={
                "class": "form-control"
            }),
        }