from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.http import Http404
from django.contrib import messages
from django.forms import formset_factory
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Prefetch
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from .models import Price, Order, Item, Type, Subject
from .forms import TypeForm, SubjectForm, LevelForm, PriceForm, ItemFormSet, ItemForm, OrderStatusForm, SelectCustomerForm
from .tasks import send_email_task
from .serializer import PriceSerializer

User = get_user_model()

class Pricing(View):

    def make_context(self):
        """ To update context for get and post methods. """
        forms = {
                'type_form': TypeForm(),
                'level_form': LevelForm(),
                'subject_form': SubjectForm(),
                'price_form': PriceForm(),
            }
        prices = Price.objects.all().order_by('type__type', 'subject__subject', 'level__level_num', 'min_range')
        self.context = {
            'forms': forms,
            'prices': prices,
            }
    
    def invalid_form(self, request, form_name: str, form):
        """ The specific form will be populated with the data previously submitted. """
        context = self.context
        context['forms'][form_name] = form
        return render(request, "shop/pricing.html", context)

    def get(self, request):
        self.make_context()
        return render(request, "shop/pricing.html", self.context)
    
    def post(self, request):
        self.make_context()

        if 'type_form' in request.POST:
            form = TypeForm(request.POST)
            if form.is_valid():
                form.save()
                return render(request, "shop/pricing.html", self.context)
            return self.invalid_form(request, 'type_form', form)
            
        elif 'level_form' in request.POST:
            form = LevelForm(request.POST)
            if form.is_valid():
                form.save()
                return render(request, "shop/pricing.html", self.context)
            return self.invalid_form(request, 'level_form', form)
        
        elif 'subject_form' in request.POST:
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
                return render(request, "shop/pricing.html", self.context)
            return self.invalid_form(request, 'subject_form', form)

        elif 'price_form' in request.POST:
            form = PriceForm(request.POST)
            if form.is_valid():
                new_price = form.save(commit=False)
                new_price.type = new_price.subject.type
                new_price.save()
                return render(request, "shop/pricing.html", self.context)
            return self.invalid_form(request, 'price_form', form)
        
class EditPrice(View):

    def get_model(self, price_id):
        try:
            price = Price.objects.get(id=price_id)
        except Price.DoesNotExist:
            raise Http404
        return price
    
    def get(self, request, price_id):
        price = self.get_model(price_id)
        form = PriceForm(instance=price)
        return render(request, "shop/edit_price.html", {'form': form})
        
    def post(self, request, price_id):
        price = self.get_model(price_id)
        form = PriceForm(instance=price, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'قیمت با موفقیت تغییر کرد.')
        return redirect("shop:pricing")

class EditPriceAPIView(APIView):
    def get_object(self, price_id):
        try:
            price = Price.objects.get(id=price_id)
        except Price.DoesNotExist:
            raise Http404
        return price
        
    def get(self , request: Request, price_id):
        price = self.get_object(price_id=price_id)
        serializer = PriceSerializer(price)
        data = serializer.data
        return Response(data, status.HTTP_200_OK)
    
    def post(self, request: Request, price_id):
        price = self.get_object(price_id=price_id)
        serializer = PriceSerializer(instance=price, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": "The price has been updated."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class BaseCart(View):

    def get_cart_items(self):
        formset = formset_factory(ItemForm, extra=1)
        units = {}  # {'type.id': 'type.unit'}      Ex: {'1': 'hour'}
        subjects = {}   # {'type.id': [subjects_ids]}       Ex: {'1': [1, 4, 5]}
        subject_ids = {}    # {'subject.id': 'subject_name'}    Ex: {'1': 'news'}
        prices = {}     # {'subject.id': {'level.id': [price.min_range, price.max_range, price, discount]}}
                        # Ex: {'1': {'1': [[0, 5, 400000, 10]]}, '3': {'1': [[8, 20, 35000, 0]], '2': [[8, 20, 45000, 25]]}}

        subject_objects = Subject.objects.filter(is_available=True).prefetch_related('type')
        subject_data = []   # list for save query data and reduce number of queries.
        for subject in subject_objects:
            subject_data.append({'id': str(subject.id),
                                 'type_id': str(subject.type.id),
                                 'subject': str(subject.subject),
                                 })

        for type in Type.objects.filter(is_available=True):
            units[str(type.id)] = str(type.unit)
            subjects_id_list = []   # Temporary dic for related subjects ids
            for subject in subject_data:
                if subject['type_id'] == str(type.id):
                    subjects_id_list.append(int(subject['id']))
            subjects[str(type.id)] = subjects_id_list

        for subject in subject_data:
            subject_ids[str(subject['id'])] = str(subject['subject'])

        for price in Price.objects.filter(is_available=True).select_related('subject', 'level'):
            if str(price.subject.id) not in prices:
                prices[str(price.subject.id)] = {}
            if str(price.level.id) not in prices[str(price.subject.id)]:
                prices[str(price.subject.id)][str(price.level.id)] = []
            prices[str(price.subject.id)][str(price.level.id)].append([price.min_range, price.max_range, price.price, price.discount])

        context = {
            'formset': formset,
            'units': units,
            'subjects': subjects,
            'subject_ids': subject_ids,
            'prices': prices,
        }
        return context
    
    def send_email_to_admins(self):
        subject = "سفارش جدید"
        message = "سلام. سفارش جدیدی در سایت ثبت شده است. ارسال شده با redis."
        admin_emails = list(User.objects.filter(is_admin=True).values_list('email', flat=True))
        send_email_task.delay(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            admin_emails,
            fail_silently=False,
        )
        print(f"emial sent to {admin_emails}")

    def make_order(self, request, customer, ordered_by_admin):
        ItemFormSet = formset_factory(ItemForm)
        formset = ItemFormSet(request.POST)
        order_description = request.POST.get('order-description', ' ')
        if formset.is_valid():
            order = Order.objects.create(customer=customer, price=0, description=order_description)
            order_price = 0
            print(formset.cleaned_data)
            for form in formset:
                type = form.cleaned_data['type']
                try:
                    subject = Subject.objects.get(id=form.cleaned_data['subject'])
                except:
                    raise Http404
                level = form.cleaned_data['level']
                number = form.cleaned_data['number']
                unit_price = Price.objects.filter(
                    type=type,
                    subject=subject,
                    level=level,
                    min_range__lte=number,
                    max_range__gte=number,
                    is_available=True,
                ).first()
                item_price = unit_price.price * (1 - unit_price.discount/100) * number
                item = Item.objects.create(
                    type=type,
                    subject=subject,
                    level=level,
                    number=number,
                    item_price=item_price,
                    order=order,
                )
                order_price += item_price
            order.price = order_price
            if ordered_by_admin:
                order.ordered_by_admin = True
            order.save()
            messages.success(request, 'سفارش شما ایجاد شد.')
            if not ordered_by_admin:
                self.send_email_to_admins()
            return True
        return False

    
@method_decorator(login_required, name='dispatch')
class CartByCustomer(BaseCart):
    def get(self, request):
        return render(request, "shop/cart.html", self.get_cart_items())
    
    def post(self, request):
        self.make_order(request, customer=request.user, ordered_by_admin=False)
        return redirect("shop:orders")


@method_decorator(login_required, name='dispatch')
class CartByAdmin(PermissionRequiredMixin, BaseCart):
    permission_required = 'shop.add_order'

    def get(self, request):
        context = self.get_cart_items()
        context['by_admin'] = True
        context['select_customer_form'] = SelectCustomerForm()
        return render(request, "shop/cart.html", context)
    
    def post(self, request):
        try:
            customer = User.objects.get(id=request.POST.get('customer'))
        except:
            raise Http404
        self.make_order(request, customer=customer, ordered_by_admin=True)
        return redirect("shop:all_orders")

    
@method_decorator(login_required, name='dispatch')
class Orders(View):
    """ Show orders of specific user """
    def get(self, request):
        orders = Order.objects.filter(customer=request.user).order_by('-purchase_date').prefetch_related(
            Prefetch('items', queryset=Item.objects.select_related('type', 'subject', 'level'))
        )
        return render(request, 'shop/orders.html', {'orders': orders})
    

class AllOrders(PermissionRequiredMixin, View):
    """ Show all orders to manager """
    permission_required = 'shop.change_order_status'

    def get(self, request):
        orders = Order.objects.all().order_by('status').select_related('customer').prefetch_related(
            Prefetch('items', queryset=Item.objects.select_related('type', 'subject', 'level'))
        )
        form = OrderStatusForm()
        context = {'orders': orders, 'form': form}
        return render(request, 'shop/all_orders.html', context)
    
    def post(self, request):
        form = OrderStatusForm(data=request.POST)
        if form.is_valid():
            try:
                order = Order.objects.get(id=form.cleaned_data['order_id'])
            except Order.DoesNotExist:
                raise Http404
            order.status = form.cleaned_data['status']
            order.save()
            messages.success(request, 'وضعیت سفارش تغییر کرد.')
            if order.customer.receive_email:
                order_status = order.get_order_status(int(form.cleaned_data['status']))
                subject = "تغییر وضعیت سفارش"
                message = f"وضعیت سفارش شما به «{order_status}» تغییر کرد."
                customer_email = [order.customer.email, ]
                send_email_task.delay(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    customer_email,
                    fail_silently=False,
                )

        return redirect("shop:all_orders")

