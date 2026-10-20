
"""
URL routes for Shopora account functionality.
"""

from django.urls import path

from . import views


urlpatterns = [
    # Customer registration
    path(
        "register/",
        views.register,
        name="register",
    ),

    # Customer login
    path(
        "login/",
        views.user_login,
        name="login",
    ),

    # Customer logout
    path(
        "logout/",
        views.user_logout,
        name="logout",
    ),

    # Customer profile
    path(
        "profile/",
        views.account_profile,
        name="account_profile",
    ),
]
