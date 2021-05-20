from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

from user.models import User

upload_storage = FileSystemStorage(location=settings.UPLOAD_FILE_DIR)


def save_uploaded_file(instance, filename):
    return instance.parsed_file_name


class Upload(models.Model):
    uploaded_file_name = models.CharField(max_length=250)
    file = models.FileField(upload_to=save_uploaded_file, storage=upload_storage, max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parsed_file_name = models.CharField(max_length=100, default="Uploaded_file")
    prediction = models.CharField(max_length=100, default="")
    status = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
