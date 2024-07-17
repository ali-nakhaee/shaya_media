""" users.views """

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from . import forms

class LoginPage(View):
    """ Main login page """
    def get(self, request):
        form = forms.LoginForm()
        context = {'form': form}
        return render(request, 'users/login.html', context)

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('blog:post_list')
            else:
                 messages.error(request, 'Login failed.')
