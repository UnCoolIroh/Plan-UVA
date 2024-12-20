from django import forms
from .models import *

from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    keywords = forms.CharField(
        required=False,
        help_text="Enter keywords separated by commas (optional)."
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text="Enter a description for the document (optional)."
    )

    file_name = forms.CharField(
        required=False,
        help_text="Enter a name for the file (optional)."
    )

    file = forms.FileField(
        required=False,
        help_text="Select a file to upload."
    )

    class Meta:
        model = Document
        fields = ['file', 'file_name', 'description', 'keywords']

    def clean(self):
        cleaned_data = super().clean()
        file_name = cleaned_data.get('file_name')
        file = self.files.get('file')  # Access the uploaded file

        if file and not file_name:
            cleaned_data['file_name'] = file.name

        # If no file is uploaded, ensure file_name is set to None
        if not file:
            cleaned_data['file_name'] = None

        return cleaned_data


class CreateConversationForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'searchable-select'}),
        required=True,
        label="Select Users"
    )

    class Meta:
        model = Conversation
        fields = ['users']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project_group
        fields = ['name', 'description']

from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    text = forms.CharField(
        required=False,  # Make this field optional
        widget=forms.Textarea(attrs={'placeholder': 'Type your message here (optional)'}),
    )

    class Meta:
        model = Message
        fields = ['text']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'assigned_users', 'weight', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and weight > 10:
            raise forms.ValidationError('Weight cannot be more than 10.')
        return weight