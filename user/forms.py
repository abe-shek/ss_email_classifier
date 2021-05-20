import re

from django import forms
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form

from .models import User

REG_EX = ("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&_-]{8,20}$")


class LoginForm(Form):
    username = forms.CharField(max_length=15)
    password = forms.CharField(max_length=256, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "username", "required": True}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "password", "required": True}
        )


class RegisterForm(ModelForm):
    input_password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "placeholder": field.label})

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already in use")
        if "_" in username:
            raise ValidationError("Username cannot contain _")
        return username

    def clean_email_address(self):
        email_address = self.cleaned_data["email"]
        if User.objects.filter(email=email_address).exists():
            raise ValidationError("Email already in use")
        return email_address

    def clean_input_password(self):
        input_password = self.cleaned_data["input_password"]
        pattern = re.compile(REG_EX)
        if re.search(pattern, input_password):
            return input_password
        else:
            raise ValidationError("Password requirements don't match")

    def clean_confirm_password(self):
        if "input_password" not in self.cleaned_data:
            return ValidationError("Password not valid")
        input_password = self.cleaned_data["input_password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if input_password and confirm_password:
            if input_password != confirm_password:
                raise ValidationError("Passwords do not match")
        return confirm_password

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "mail_address",
            "occupation",
            "phone_number",
            "input_password",
            "confirm_password",
        ]
        exclude = ["password"]
        widgets = {"mail_address": forms.Textarea(attrs={"rows": 5})}


class ChangePasswordForm(Form):
    current_password = forms.CharField(max_length=256, widget=forms.PasswordInput)
    input_password = forms.CharField(max_length=256, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=256, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "placeholder": field.label})

    def clean_current_password(self):
        username = self.data.get("username", None)
        if not username:
            raise ValidationError("You must login to change passwords")

        user = User.objects.all().filter(username=username).first()
        if not user:
            raise ValidationError("Invalid user account")

        current_password = self.cleaned_data["current_password"]
        if not check_password(current_password, user.password):
            raise ValidationError("Current password doesn't match")

        return current_password

    def clean_input_password(self):
        if "current_password" not in self.cleaned_data:
            raise ValidationError("Current password doesn't match")
        input_password = self.cleaned_data["input_password"]
        pattern = re.compile(REG_EX)
        if re.search(pattern, input_password):
            return input_password
        else:
            raise ValidationError("Password requirements don't match")

    def clean_confirm_password(self):
        if "input_password" not in self.cleaned_data:
            raise ValidationError("Password not valid")
        input_password = self.cleaned_data["input_password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if input_password and confirm_password:
            if input_password != confirm_password:
                raise ValidationError("Passwords do not match")
        return confirm_password
