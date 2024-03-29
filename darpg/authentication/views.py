from django.contrib.auth import (authenticate, get_user_model, login, logout)
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.shortcuts import (redirect, render)
from django.contrib.auth.decorators import login_required

from .forms import CustomLoginForm, RegisterForm, ForgetPasswordEmailCodeForm, ChangePasswordForm, OtpForm
from .models import OtpCode, CustomUser
from .utils import send_activation_code, send_reset_password_code
from .decorators import only_authenticated_user, redirect_authenticated_user

@only_authenticated_user
def home_view(request):
    return render(request, 'auth/user.html')

@redirect_authenticated_user
def signin_view(request):
    error = None
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username_or_email'], password=form.cleaned_data['password'])
            if user:
                if not user.is_active:
                    messages.warning(request, _(f"Its look like you haven't still verified your email - {user.email}"))
                    return redirect('users:activate_email')
                else:
                    login(request, user)
                    return redirect('/home')
            else:
                error = 'Invalid credentials'
        
    return render(request, 'auth/signin.html', {'error': error})
    
@only_authenticated_user
@login_required
def logout_view(request):
    logout(request)
    return redirect('auth:signin')

@redirect_authenticated_user
def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.source = 'Register'
            user.save(True)

            code = get_random_string(20)
            otp = OtpCode(code=code, user=user)
            otp.save(True)

            try:
                send_activation_code(user.email, code)
            except:
                otp.delete()
                user.delete()
                messages.error(request, _('Failed to Activation send code'))
            else:
                messages.success(request, _(f'We have sent a verification code to your email - {user.email}'))
                return redirect('auth:activate_email')
        else:
            for err_msg in form.error_messages.values():
                messages.error(request, err_msg)
            
    return render(request, 'auth/signup.html', {})

@redirect_authenticated_user
def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgetPasswordEmailCodeForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            user = get_user_model().objects.get(**username_or_email)
            code = get_random_string(20)

            otp = OtpCode(code=code, user=user, email=user.email)
            otp.save()

            try:
                send_reset_password_code(user.get_email_field_name, code)
            except:
                otp.delete()
                messages.error(request, _('Failed to send code'))
            else:
                messages.success(request, _(f'We have sent a password reset OTP to your email - {user.email}'))
                return redirect('auth:reset_code')
        else:
            for err_msg in form.error_messages.values():
                messages.error(request, err_msg)    
    return render(request, 'auth/forgot_password.html', {})

@redirect_authenticated_user
def check_otp_view(request):
    if request.method == 'POST':
        form = OtpForm(request.POST)
        if form.is_valid():
            otp = OtpCode.objects.get(code=form.cleaned_data['otp'])
            user = otp.user
            otp.delete()
            user.is_active = True
            user.save()
            return redirect('auth:signin')
        else:
            for err_msg in form.error_messages.values():
                messages.error(request, err_msg)

    return render(request, 'auth/user_otp.html', {})

@redirect_authenticated_user
def check_reset_otp_view(request):
    if request.method == 'POST':
        form = OtpForm(request.POST)
        if form.is_valid():
            otp = OtpCode.objects.get(code=form.cleaned_data['otp'])
            request.session['email'] = otp.user.email
            messages.success(request, _("Please create a new password that you don't use on any other site."))
            return redirect('auth:reset_new_password')
        else:
            for err_msg in form.error_messages.values():
                messages.error(request, err_msg)
    return render(request, 'auth/user_otp.html', {})

@redirect_authenticated_user
def reset_new_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            email = request.session['email']
            del request.session['email']
            user = CustomUser.objects.get(email=email)
            user.password = make_password(form.cleaned_data['new_password2'])
            user.save()
            messages.success(request, _("Your password changed. Now you can login with your new password."))
            return redirect('auth:signin')
        else:
            for err_msg in form.error_messages.values():
                messages.error(request, err_msg)
    return render(request, 'auth/new_password.html', {})