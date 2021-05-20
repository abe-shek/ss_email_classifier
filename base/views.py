from rest_framework.response import Response


def load_confirm_modal(action_url, title="Confirm", body=""):
    context = {
        "action_url": action_url,
        "modal_title": title,
        "modal_body": body if body else "",
    }
    return Response(context, template_name="base/confirm_modal.html")


def load_success_modal(success_msg, extra_msgs=None):
    context = {"success_message": success_msg, "messages": extra_msgs}
    return Response(context, template_name="base/success_modal.html")


def load_error_modal(error_message, errors=None):
    context = {"error_message": error_message, "errors": errors}
    return Response(context, template_name="base/error_modal.html")
