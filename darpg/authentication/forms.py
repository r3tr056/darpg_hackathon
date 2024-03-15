from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django import forms
from authentication.models import OtpCode

class CustomLoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=256)
    password = forms.CharField()

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data['username_or_email']
        if '@' in username_or_email:
            validate_email(username_or_email)
            data = {'email': username_or_email}
        else:
            data = {'username': username_or_email}
        try:
            get_user_model().objects.get(**data)
        except get_user_model().DoesNotExist:
            raise ValidationError(_("This {} does not exist".format(list(data.keys())[0])))
        else:
            return username_or_email
        
class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = widgets.TextInput()
        self.fields['email'].widget = widgets.TextInput()
        self.fields['password1'].widget = widgets.PasswordInput()
        self.fields['password2'].widget = widgets.PasswordInput()

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("This email address is already exists.")
        return email
    
    class Meta:
        model = get_user_model()
        fields = ("username", "email")

class ForgetPasswordEmailCodeForm(forms.Form):
    username_or_email = forms.CharField(max_length=256)

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data['username_or_email']
        data = {'username': username_or_email}

        if '@' in username_or_email:
            validate_email(username_or_email)
            data = {'email': username_or_email}
        try:
            get_user_model().objects.get(**data)
        except get_user_model().DoesNotExist:
            raise ValidationError(f'There is not account with this {list(data.keys())[0]}')
    
        if not get_user_model().objects.get(**data).is_active:
            raise ValidationError(_("This account is not active."))
        return data
        
class ChangePasswordForm(forms.Form):
    new_password1 = forms.CharField(label='New password')
    new_password2 = forms.CharField(label="Confirm Password")

    def clean_new_password2(self):
        password1 = self.cleaned_data['new_password1']
        password2 = self.cleaned_data['new_password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Passwords do not match'))
        password_validation.validate_password(password2)
        return password2
    
class OtpForm(forms.Form):
    otp = forms.CharField()

    def clean_otp(self):
        otp_code = self.cleaned_data['otp']
        try:
            OtpCode.objects.get(code=otp_code)
        except OtpCode.DoesNotExist:
            raise ValidationError(_('You have entered incorrect code!'))
        else:
            return otp_code