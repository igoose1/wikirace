from django.forms import ModelForm, Textarea
from .models import Feedback


class FeedbackForm(ModelForm):
    """
        Class represents feedback form
        Uses to rendering and getting data from form
    """
    class Meta:
        model = Feedback
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
        labels = {
            'text': 'Отзыв'
        }
