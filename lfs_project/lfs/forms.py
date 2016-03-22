from django import forms
from lfs.models import Teacher, Module, ContentFile, Page
from django.contrib.auth.models import User
from passwords.fields import PasswordField

class UserForm(forms.ModelForm):
	password = PasswordField(label="Password", widget=forms.PasswordInput())
	terms = forms.BooleanField(required=True, error_messages={'required': 'You must accept the terms and conditions'}, label="I have read and agree to the terms and conditions")
	

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password')

class TeacherForm(forms.ModelForm):

	bio = forms.CharField(widget=forms.Textarea, initial = '')
	school = forms.CharField(max_length = 200, initial = '', required = False)
	AGE_RANGE_CHOICES = (
        ('0', '16-21'),
        ('1', '22-28'),
        ('2', '29-35'),
        ('3', '36-42'),
        ('4', '42-48'),
        ('5', '49-55'),
        ('6', '56 or older'),
    )
	age_range = forms.ChoiceField(choices = AGE_RANGE_CHOICES)
	location = forms.CharField(max_length=200, initial='', required = False)
	picture = forms.ImageField(required = False)
	leaderboard = forms.BooleanField(required=False, label="I allow my information (name, age-range, location, progress) to be shown in the leaderboard")
    
	class Meta:
		model = Teacher
		exclude = ('user',)

class ModuleForm(forms.ModelForm):
    title = forms.CharField(max_length=200)
    background = forms.ImageField(required = False)

    class Meta:
    	model = Module
    	exclude = ('taker',)


class ContentForm(forms.ModelForm):
    file = forms.FileField(required = True)

    class Meta:
        model = ContentFile
        exclude = ('module', 'clicks')


class PageForm(forms.ModelForm):
    section = forms.CharField(max_length=200) # title of section
    content = forms.CharField(widget=forms.Textarea, initial = '')

    class Meta:
        model = Page
        exclude = ('module','time',)
