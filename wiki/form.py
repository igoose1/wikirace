from django.forms import ModelForm, Textarea
from .models import Feedback


class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'text']
        widgets = {
            'name': Textarea(attrs={'cols': 80, 'rows': 1}),
            'text': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
        labels = {
            'name': 'Имя',
            'text': 'Отзыв'
        }
