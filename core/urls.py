from django.urls import path, reverse_lazy
from . import views

from .forms import LoginForm, MyPasswordResetForm, MySetPasswordForm
from django.contrib.auth import views as authView

app_name = 'core'

urlpatterns = [
    path('', views.welcome_page, name='welcome_page'),

    path('signup/', views.signup, name='signup'),

    path('login/', authView.LoginView.as_view(
        template_name = 'core/login_form.html',
        authentication_form = LoginForm
    ), name='login'),

    path('logout/', authView.LogoutView.as_view(), name='logout'),

    path('password-reset/', authView.PasswordResetView.as_view(
        template_name='core/password_reset.html',
        email_template_name='core/password_reset_email.html',
        form_class=MyPasswordResetForm,
        success_url= reverse_lazy('core:password_reset_done')
    ), name='password_reset'),

    path('password-reset-done/', authView.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html'
    ), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', authView.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html',
        form_class=MySetPasswordForm,
        success_url = reverse_lazy('core:password_reset_complete')
    ), name='password_reset_confirm'),

    path('password-reset-complete/', authView.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'
    ), name='password_reset_complete'),
]