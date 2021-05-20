import os
import time

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from base.views import load_success_modal, load_error_modal
from classifier.forms import UploadFileForm
from classifier.models import Upload
from model.model import init_model
from user.views import validate_n_get_user
from base.utils import UploadFileType, Error, ErrorCodes, UploadStatus, Directory


def classify_document(request):
    is_valid, user, context = validate_n_get_user(request)
    if not is_valid:
        return redirect("user:logout_user")
    init_model()
    return render(request, 'classifier/overview.html', context)


class ResultHistory(ListView):
    template_name = "classifier/history.html"
    context_object_name = "results"
    paginate_by = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None

    def get(self, *args, **kwargs):
        is_valid, self.user, _ = validate_n_get_user(self.request)
        if not is_valid:
            return redirect("user:logout_user")
        return super(ResultHistory, self).get(*args, **kwargs)

    def get_queryset(self):
        is_valid, self.user, _ = validate_n_get_user(self.request)
        if not is_valid:
            return []
        return self.get_results()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ResultHistory, self).get_context_data(**kwargs)
        is_valid, self.user, context_ = validate_n_get_user(self.request)
        if is_valid:
            context.update(context_)
            context["paginated_by"] = self.paginate_by
        else:
            context["results"] = []
        return context

    def get_paginate_by(self, queryset):
        self.paginate_by = int(self.request.GET.get("paginate_by", 10))
        return self.paginate_by

    def get_results(self):
        if not self.user:
            return []
        results = Upload.objects.all().filter(user=self.user)
        for res in results:
            if res.status == UploadStatus.UP_STATUS_PROCESSING:
                res.status_str = "Processing your file"
            elif res.status == UploadStatus.UP_STATUS_PROCESSED:
                res.status_str = "Processed successfully"
            elif res.status == UploadStatus.UP_STATUS_ERROR:
                res.status_str = "Processing failed with error"
            elif res.status == UploadStatus.UP_STATUS_NOT_UPLOADED:
                res.status_str = "Not uploaded"
        return results


@api_view(["GET", "POST"])
@renderer_classes([TemplateHTMLRenderer])
def upload_files(request):
    is_valid, user, context = validate_n_get_user(request)
    if not is_valid:
        return redirect("user:logout_user")
    context.update({
        "action_url": reverse("classifier:upload_files"),
    })

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('upload_file')
            print(files)
            return process_uploaded_file(user, files)
    else:
        form = UploadFileForm()

    context['form'] = form
    context["modal_title"] = "Upload Files"
    return Response(context, template_name="classifier/upload_modal.html")


def create_upload_obj(user, file):
    parsed_name = f"{user.username}_{int(time.time_ns())}{UploadFileType.FT_TEXT_EXT}"
    file_obj = {
        "user": user,
        "uploaded_file_name": file.name,
        "parsed_file_name": parsed_name,
        "status": UploadStatus.UP_STATUS_PROCESSING,
        "file": file
    }
    upload_obj = Upload.objects.create(**file_obj)
    upload_obj.parsed_file_name = f"{upload_obj.id}_{upload_obj.parsed_file_name}"
    upload_obj.save()
    rename_queue_file(os.path.join(Directory.DIR_Q_PATH, parsed_name),
                      os.path.join(Directory.DIR_Q_PATH,upload_obj.parsed_file_name))
    return upload_obj


def process_uploaded_file(user, files):
    try:
        for file in files:
            create_upload_obj(user, file)
    except BaseException as error:
        errors = [Error(ErrorCodes.E_METHOD_CALL_FAILED,
                        f"Processing the uploaded files failed with {error}")]
        return load_error_modal("Sorry, we couldn't complete this operation. "
                                "Please check the errors listed below for more details "
                                "and contact IT if the problem persists.", errors)

    return load_success_modal(f"Hurray!! Your {len(files)} file(s) were uploaded successfully. "
                              f"Allow us a couple of minutes to process them and we'll have "
                              f"their categories under the 'Results' section soon!")


def rename_queue_file(current, new):
    if not os.path.exists(current):
        return
    try:
        os.rename(current, new)
    except BaseException as err:
        print(err)