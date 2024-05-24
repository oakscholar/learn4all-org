from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import *
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}))
    # phone = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone', 'class': 'form-control'}))

    class Meta(UserCreationForm):
        model = CustomUser
        # fields = UserCreationForm.Meta.fields + ("phone",)
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user
    
class EmailLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))

class UsernameLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))

        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class GoalForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['goal']

    def __init__(self, *args, **kwargs):
        super(GoalForm, self).__init__(*args, **kwargs)
        self.fields['goal'].required = True


class LearningStyleForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['learning_style']

    def __init__(self, *args, **kwargs):
        super(LearningStyleForm, self).__init__(*args, **kwargs)
        self.fields['learning_style'].required = True

class TimeCommitmentForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['learning_wks', 'learning_hrs_per_wk']

class SkillForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['skill']

    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__(*args, **kwargs)
        self.fields['skill'].required = True