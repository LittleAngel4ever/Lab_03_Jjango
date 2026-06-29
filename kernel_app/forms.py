from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class RegistrationForm(UserCreationForm):
    pass

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class NewCard(forms.Form):
    photo = forms.FileField(max_length=500, label='Фото')
    artist = forms.CharField(max_length=200, label='Исполнитель')
    title = forms.CharField(max_length=200, label='Название трека')
    genre = forms.CharField(max_length=100, label='Жанр')
    release_year = forms.IntegerField(label='Год выпуска')