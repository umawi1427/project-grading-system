from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from .models import Project, Profile
from django.core.validators import RegexValidator

class CustomSetPasswordForm(SetPasswordForm):
    new_password2 = None

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        return password1

class ProjectForm(forms.ModelForm):
    name = forms.CharField(
        validators=[
            RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.'),
            RegexValidator(r'^.{4,}$', 'Minimum 4 characters required.')
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'minlength': '4'}),
        required=True
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'resize:none;'}),
        required=True
    )
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__major='teacher'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select a teacher',
        required=True
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'custom-file-input'}),
        required=True
    ) 
    grade = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'teacher', 'file']
        
class GradeForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['grade']
        widgets = {
            'grade': forms.NumberInput(attrs={'class': 'form-control'}),
        }