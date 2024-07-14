from django.urls import path
from .views import AuthView, login_page, logout_view


urlpatterns = [
    path(
        "login/",
       login_page,
        name="auth-login-basic",
    ),
    path("",login_page, name="login"),
    path("logout",logout_view,name="logout"),
    path(
        "auth/register/",
        AuthView.as_view(template_name="auth_register_basic.html"),
        name="auth-register-basic",
    ),
    path(
        "auth/forgot_password/",
        AuthView.as_view(template_name="auth_forgot_password_basic.html"),
        name="auth-forgot-password-basic",
    ),
]
