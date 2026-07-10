from django import forms

from .models import Post, Thread

INPUT = 'form-input'


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title']
        labels = {'title': 'Thementitel'}
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT,
                'placeholder': 'Geben Sie den Thementitel ein',
            }),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        labels = {'content': 'Ihre Nachricht'}
        widgets = {
            'content': forms.Textarea(attrs={
                'class': INPUT,
                'rows': 5,
                'placeholder': 'Geben Sie Ihre Nachricht ein …',
            }),
        }

    def clean_content(self):
        content = self.cleaned_data['content'].strip()
        if not content:
            raise forms.ValidationError('Der Beitrag darf nicht leer sein.')
        return content
