from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    """
        Class represents feedback form
        Uses to rendering and getting data from form
    """
    class Meta:
        model = Feedback
        fields = ['text']
