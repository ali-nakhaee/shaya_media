""" users.forms """

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=150, label=_("شماره همراه"))
    password = forms.CharField(max_length=150, widget=forms.PasswordInput, label=_("رمز موقت"), required=False)


class SignupForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("رمز عبور"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=_("رمز عبور نمی‌تواند مشابه دیگر اطلاعات کاربری شما باشد." '\n'
                    "رمز عبور باید حداقل ۸ کاراکتر داشته باشد." '\n'
                    "رمز عبور نمی‌تواند از رمزهای رایج باشد." '\n'
                    "رمز عبور نمی‌تواند تماما عدد باشد."),
    )
    password2 = forms.CharField(
        label=_("ورود مجدد رمز عبور"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("برای تایید رمز عبور مجددا آن را وارد کنید."),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'phone_number')
        labels = {'username': 'نام کاربری', 'first_name': 'نام', 'last_name': 'نام خانوادگی'}


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone_number', 'receive_sms', 'email', 'receive_email')
        labels = {
            'phone_number': 'شماره همراه',
            'receive_sms': 'دریافت پیامک',
            'email': 'ایمیل',
            'receive_email': 'دریافت ایمیل',
        }


class AddUserByAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone_number', 'admin_description')
        labels = {
            'phone_number': 'شماره همراه',
            'admin_description': 'توضیحات (صرفا توسط ادمین مشاهده می‌شود)',
        }


class ChangeAdminDescriptionForm(forms.Form):
    user_id = forms.IntegerField()
    admin_description = forms.CharField()
