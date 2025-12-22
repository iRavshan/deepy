from django import forms
from .models import Submission

class ChallangeSubmissionForm(forms.ModelForm):
    code = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'editor-layer',
        'id': 'editing-layer',
        'spellcheck': 'false'
    }))
    class Meta:
        model = Submission
        fields = ['code']