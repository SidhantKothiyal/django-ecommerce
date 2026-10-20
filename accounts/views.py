
"""
Views for Shopora account functionality.

Includes:
- User registration
- User login
- Authenticated profile
- Secure POST-only logout
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import RegistrationForm


# ==================================================
# REGISTRATION
# ==================================================

def register(request):
    if request.user.is_authenticated:
        return redirect("account_profile")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Your account was created successfully.",
            )

            return redirect("account_profile")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


# ==================================================
# LOGIN
# ==================================================

def user_login(request):
    if request.user.is_authenticated:
        return redirect("account_profile")

    next_url = (
        request.POST.get("next")
        or request.GET.get("next", "")
    )

    form = AuthenticationForm(
        request,
        data=request.POST if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())

        messages.success(
            request,
            "Login successful.",
        )

        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)

        return redirect("account_profile")

    return render(
        request,
        "registration/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


# ==================================================
# ACCOUNT PROFILE
# ==================================================

@login_required
def account_profile(request):
    return render(
        request,
        "accounts/profile.html",
    )


# ==================================================
# LOGOUT
# ==================================================

@require_POST
def user_logout(request):
    logout(request)

    messages.success(
        request,
        "You have been logged out successfully.",
    )

    return redirect("product_list")

