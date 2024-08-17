from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Room, User

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = ["host", "participants"]


class UpdateUserForm(ModelForm):
    class Meta:
        model = User
        fields = ["name", "username", "email", "bio", "avatar"]


class RegisterForm(UserCreationForm):
    usable_password = None

    class Meta:
        fields = ["name", "username", "email", "password1", "password2"]
        model = get_user_model()
