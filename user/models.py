from django.core import validators
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    username = models.CharField(unique=True, max_length=15)
    password = models.CharField(max_length=256)

    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    phone_number = PhoneNumberField(null=False, blank=False)
    email = models.EmailField(unique=True, max_length=200, validators=[validators.validate_email])
    mail_address = models.CharField(max_length=750)
    occupation = models.CharField(max_length=250)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name"]
