from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm, ChangePasswordForm
from .models import User


def login_user(request):
    if request.session.get("is_login", None):
        is_valid, user, _ = validate_n_get_user(request)
        if not is_valid:
            return redirect('user:logout_user')
        return redirect("classifier:overview")
    login_error = False
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            try:
                user = User.objects.all().filter(username=username).first()
            except ObjectDoesNotExist:
                login_error = True
            else:
                if not user or not check_password(password, user.password):
                    login_error = True
                else:
                    request.session["username"] = username
                    request.session["is_login"] = True
                    return redirect("classifier:overview")
    else:
        form = LoginForm()
    context = {"form": form, "login_error": login_error}
    return render(request, "user/login.html", context)


def register_user(request):
    if request.session.get("is_login", None):
        is_valid, user, _ = validate_n_get_user(request)
        if not is_valid:
            return redirect('user:logout_user')
        return redirect("classifier:overview")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["input_password"]
            encrypt_pwd = make_password(password)
            f = form.save(commit=False)
            f.password = encrypt_pwd
            f.save()
            return redirect("user:login_user")
    else:
        form = RegisterForm()
    context = {
        "form": form
    }
    return render(request, "user/register.html", context)


def change_password(request):
    is_valid, user, context = validate_n_get_user(request)
    if not is_valid:
        return redirect('user:logout_user')
    match_error = False
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["input_password"]
            old_password = form.cleaned_data["current_password"]
            username = request.session.get("username", None)
            encrypt_pwd = make_password(new_password)
            try:
                user = User.objects.all().filter(username=username).first()
            except ObjectDoesNotExist:
                return redirect("user:logout_user")
            else:
                if check_password(old_password, user.password):
                    user.password = encrypt_pwd
                    user.save()
                    # Todo - add a popup
                    return redirect("classifier:overview")
                else:
                    match_error = True
    else:
        form = ChangePasswordForm()
    context.update({
        "form": form,
        "match_error": match_error
    })
    return render(request, "user/change_password.html", context)


def logout_user(request):
    request.session.flush()
    return redirect("user:login_user")


def load_profile(request):
    is_valid, user, context = validate_n_get_user(request)
    if not is_valid:
        return redirect('user:logout_user')
    profile_info = [
        {"label": "Username",
         "value": user.username
         },
        {"label": "Email",
         "value": user.email
         },
        {"label": "Name (First, Middle, Last)",
         "value": f"{user.first_name} {user.middle_name} {user.last_name}"
         },
        {"label": "Phone_number",
         "value": user.phone_number
         },
        {"label": "Mail_address",
         "value": user.mail_address
         },
        {"label": "Occupation",
         "value": user.occupation
         },
    ]
    context["profile"] = profile_info
    return render(request, "user/profile.html", context)


def get_user(request):
    is_login = request.session.get("is_login", None)
    if not is_login:
        return None, None
    username = request.session.get("username", None)
    user = None
    context = {"unauth": True}
    if username:
        try:
            user = User.objects.get(username=username)
            context["unauth"] = False
        except ObjectDoesNotExist:
            context["unauth"] = True
        else:
            context["user"] = {
                "username": user.username,
                "fname": user.first_name,
                "lname": user.last_name,
                "abv_name": f"{user.first_name} {user.middle_name[0].upper()}. {user.last_name}",
            }
    return user, context


def validate_n_get_user(request=None):
    if not request:
        return False, None, None
    is_valid = False
    user, context = get_user(request)
    if user:
        is_valid = True
    return is_valid, user, context
