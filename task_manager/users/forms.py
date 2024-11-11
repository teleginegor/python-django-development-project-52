from django import forms
from django.contrib.auth.forms import UserCreationForm

from task_manager.texts import create_user
from task_manager.users.models import User


class UserForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, required=True, label=create_user['first_name']
    )
    last_name = forms.CharField(
        max_length=150, required=True, label=create_user['last_name']
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2'
        )


class UpdateUserForm(UserForm):
    def clean_username(self):
        return self.cleaned_data.get("username")
