""" users.views """

from unidecode import unidecode

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
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
            
            random_number = user.make_temporary_password()
            messages.success(request, f"رمز موقت شما: {random_number}")
            request.session['change_phone_number'] = False
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
        if form.is_valid():
            if request.session['change_phone_number']:
                phone_number = request.session['previous_phone_number']
            else:
                phone_number = form.cleaned_data['phone_number']
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                raise Http404
            
            form_password = unidecode(form.cleaned_data['password'])
            if user.check_temporary_password(form_password) == True:
                login(request, user, backend='users.backends.PhoneNumberAuthBackend')
                if request.session['change_phone_number']:
                    User.objects.filter(id=user.id).update(phone_number=request.session['phone_number'])
                    messages.success(request, 'اطلاعات شما با موفقیت تغییر کرد.')
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
        user = User.objects.get(id=request.user.id)
        previous_phone_number = user.phone_number
        if form.is_valid():
            #check if changed!
            new_phone_number = unidecode(form.cleaned_data['phone_number'])
            if previous_phone_number == new_phone_number:
                form.save()
                messages.success(request, "اطلاعات شما با موفقیت تغییر کرد.")
                return redirect('users:user_settings')
            else:
                """ The phone number has changed. Need to verify new number."""
                user.email = form.cleaned_data["email"]
                user.receive_sms = form.cleaned_data["receive_sms"]
                user.receive_email = form.cleaned_data["receive_email"]
                user.save(update_fields=['email', 'receive_sms', 'receive_email'])
                # The line above this line (update_fields) is necessary to prevent save new phone number in save method.
                request.session['change_phone_number'] = True
                request.session['previous_phone_number'] = previous_phone_number
                request.session['phone_number'] = new_phone_number
                request.session['next'] = "users:user_settings"
                random_number = user.make_temporary_password()
                messages.success(request, f"رمز موقت شما: {random_number}")
                messages.info(request, f"برای تغییر شماره همراه، پیامک ارسالی به شماره {new_phone_number} را وارد کنید.")
                return redirect('users:check_password')
        else:
            context = {'form': form}
            return render(request, 'users/user_setting.html', context)


@method_decorator(login_required, name='dispatch')
class AddUser(PermissionRequiredMixin, View):
    permission_required = "users.add_user"

    def get(self, request):
        form = forms.AddUserByAdminForm()
        context = {'form': form}
        return render(request, 'users/add_user.html', context)
    
    def post(self, request):
        form = forms.AddUserByAdminForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'کاربر با موفقیت اضافه شد.')
        else:
            messages.error(request, form.errors)
        return redirect('shop:cart_by_admin')


@method_decorator(login_required, name='dispatch')
class AllUsers(View):
    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        context = {
            'users': users,
            'form': forms.ChangeAdminDescriptionForm()
        }
        return render(request, 'users/all_users.html', context)

    def post(self, request):
        form = forms.ChangeAdminDescriptionForm(data=request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            try:
                user = User.objects.get(id=form.cleaned_data['user_id'])
            except User.DoesNotExist:
                raise Http404
            user.admin_description = form.cleaned_data['admin_description']
            user.save(update_fields=['admin_description', ])
            messages.success(request, 'یادداشت ادمین برای کاربر مدنظر تغییر کرد.')
            
        return redirect('users:all_users')

