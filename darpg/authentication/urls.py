from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view, signin_view, logout_view, signup_view, check_otp_view, check_reset_otp_view, reset_new_password_view, forgot_password_view

app_name = 'auth'

urlpatterns = [
    path('', home_view, name='home'),
    path('signin/', signin_view, name='signin'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('activate-email/', check_otp_view, name='activate_email'),
    path('reset-code/', check_reset_otp_view, name='reset_code'),
    path('new-password/', reset_new_password_view, name='reset_new_password')
]