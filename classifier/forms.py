import os

from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form

from base.utils import UploadFileType


def validate_file_extension(value, valid_ext):
    ext = os.path.splitext(value)[1]
    if ext.upper() != valid_ext.upper():
        raise ValidationError(
            u"Unsupported file extension - '%s'. "
            u"You're required to upload a file of type - "
            u"'%s'."
            % (
                ext.upper(),
                valid_ext.upper()
            )
        )


class UploadFileForm(Form):
    upload_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ["upload_file"]

    def clean_upload_file(self):
        username = self.data.get("username", None)
        if not username:
            raise ValidationError("You must be logged in to upload a file for classification!")

        # data = self.cleaned_data['upload_file']
        # Todo - update
        # maybe have a validation check for the type of files
        # for f in self.files:
        #     validate_file_extension(f, UploadFileType.FT_TEXT_EXT)

        return self.files
