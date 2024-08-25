""" users.views """

import random

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages

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
            phone_number = form.cleaned_data['phone_number']
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                user = User.objects.create(phone_number=phone_number)
            user.temporary_password = random.randint(1000, 9999)
            user.save()
            messages.success(request, f"رمز موقت شما: {user.temporary_password}")
            request.session['phone_number'] = phone_number
            return redirect('users:check_password')
        
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
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['phone_number'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                print(request.POST.get('next'))
                return redirect(self.request.POST.get('next'))
            else:
                messages.error(request, 'ورود ناموفق. رمز عبور یا نام کاربری اشتباه است.')
                return render(request, 'users/login.html', {'form':form})
            
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
