""" users.views """

import random
import hashlib
import string
from datetime import datetime
from unidecode import unidecode

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponseForbidden

from . import forms

User = get_user_model()


class LoginPage(View):
    """ Main login page """
    def get(self, request):
        form = forms.LoginForm()
        context = {'form': form,
                   'check_password': False,
                   }
        return render(request, 'users/login.html', context)
    
    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            phone_number = unidecode(form.cleaned_data['phone_number'])
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                user = User.objects.create(phone_number=phone_number)
            # random_number = random.randint(1000, 9999)
            # salt = ''.join(random.choices(string.ascii_letters, k=10))
            # hash_object = hashlib.sha256((str(random_number) + salt).encode('utf-8'))  
            # hex_dig = hash_object.hexdigest()
            # user.temporary_password = hex_dig
            # user.salt = salt
            # user.password_generation_time = timezone.now()
            # user.save()
            random_number = user.make_temporary_password()
            messages.success(request, f"رمز موقت شما: {random_number}")
            request.session['phone_number'] = phone_number
            request.session['next'] = request.POST.get('next')
            return redirect('users:check_password')
        else:
            context = {'form': form,
                       'check_password': False,
                       }
            return render(request, 'users/login.html', context)


class CheckPassword(View):
    def get(self, request):
        phone_number = request.session.get('phone_number')
        form = forms.LoginForm(initial={'phone_number': phone_number})
        context = {'form': form,
                   'check_password': True,
                   }
        return render(request, 'users/login.html', context)

    def post(self, request):
        form = forms.LoginForm(request.POST)
        print(f"form.errors: {form.errors}")
        if form.is_valid():
            try:
                user = User.objects.get(phone_number=form.cleaned_data['phone_number'])
            except User.DoesNotExist:
                raise Http404
            form_password = unidecode(form.cleaned_data['password'])
            # hash_object = hashlib.sha256((str(form_password) + user.salt).encode('utf-8'))
            # hex_dig = hash_object.hexdigest()
            # delta_time = (datetime.now().astimezone() - user.password_generation_time).total_seconds()
            # if (user.temporary_password == hex_dig) and (delta_time < 120):     # Check password and its generation time
            if user.check_temporary_password(form_password) == True:
                login(request, user, backend='users.backends.PhoneNumberAuthBackend')
                if request.session.get('next'):
                    return redirect(request.session.get('next'))
                else:
                    return redirect('shop:orders')
            else:
                messages.error(request, 'ورود ناموفق. رمز عبور اشتباه است.')
                return redirect('users:login')
        else:
            return redirect('users:login')


class Logout(View):
    def get(self, request):
        logout(request)
        return render(request, 'users/logged_out.html')


class Register(View):
    """ Register a new user """
    def get(self, request):
        form = forms.SignupForm()
        return render(request, 'users/register.html', {'form': form})
    
    def post(self, request):
        form = forms.SignupForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user, backend='users.backends.PhoneNumberAuthBackend')
            return redirect('blog:post_list')
        else:
            print(form.errors)


@method_decorator(login_required, name='dispatch')
class UserSetting(View):
    """ Change email address, phone number and ... for any user """
    def get(self, request):
        form = forms.UserSettingsForm(instance=request.user)
        context = {'form': form}
        return render(request, 'users/user_setting.html', context)
    
    def post(self, request):
        form = forms.UserSettingsForm(instance=request.user, data=request.POST)
        if form.is_valid():
            if request.user.phone_number == unidecode(form.cleaned_data['phone_number']):
                form.save()
                messages.success(request, "اطلاعات شما با موفقیت تغییر کرد.")
                return redirect('users:user_settings')
            else:
                request.user.email = form.cleaned_data["email"]
                request.user.receive_sms = form.cleaned_data["receive_sms"]
                request.user.receive_email = form.cleaned_data["receive_email"]
                request.user.save()

