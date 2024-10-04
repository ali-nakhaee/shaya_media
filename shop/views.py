from django.shortcuts import render, redirect
from django.views import View
from django.http import Http404
from django.contrib import messages
from django.forms import formset_factory
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Prefetch

from .models import Price, Order, Item, Type, Subject
from .forms import TypeForm, SubjectForm, LevelForm, PriceForm, ItemFormSet, ItemForm, OrderStatusForm

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


@method_decorator(login_required, name='dispatch')
class Cart(View):

    def get(self, request):
        formset = formset_factory(ItemForm, extra=1)
        units = {}  # {'type.id': 'type.unit'}      Ex: {'1': 'hour'}
        subjects = {}   # {'type.id': [subjects_ids]}       Ex: {'1': [1, 4, 5]}
        subject_ids = {}    # {'subject.id': 'subject_name'}    Ex: {'1': 'news'}
        prices = {}     # {'subject.id': {'level.id': [price.min_range, price.max_range, price]}}
                        # Ex: {'1': {'1': [[0, 5, 400000]]}, '3': {'1': [[8, 20, 35000]], '2': [[8, 20, 45000]]}}

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
            prices[str(price.subject.id)][str(price.level.id)].append([price.min_range, price.max_range, price.price])

        context = {
            'formset': formset,
            'units': units,
            'subjects': subjects,
            'subject_ids': subject_ids,
            'prices': prices,
        }
        
        return render(request, "shop/cart.html", context)

    def post(self, request):
        ItemFormSet = formset_factory(ItemForm)
        formset = ItemFormSet(request.POST)
        if formset.is_valid():
            order = Order.objects.create(buyer=request.user, price=0)
            order_price = 0
            print(formset.cleaned_data[0])
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
                ).first().price
                item_price = unit_price * number
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
            order.save()
            messages.success(request, 'سفارش شما ایجاد شد.')
        return redirect("shop:orders")
    

@method_decorator(login_required, name='dispatch')
class Orders(View):
    """ Show orders of specific user """
    def get(self, request):
        orders = Order.objects.filter(buyer=request.user).order_by('-purchase_date').prefetch_related(
            Prefetch('items', queryset=Item.objects.select_related('type', 'subject', 'level'))
        )
        return render(request, 'shop/orders.html', {'orders': orders})
    

class AllOrders(PermissionRequiredMixin, View):
    """ Show all orders to manager """
    permission_required = 'shop.change_order_status'

    def get(self, request):
        orders = Order.objects.all().order_by('status').select_related('buyer').prefetch_related(
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
        return redirect("shop:all_orders")

