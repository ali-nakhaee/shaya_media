from django.shortcuts import render, redirect
from django.views import View
from django.http import Http404
from django.contrib import messages

from .models import Price, Order, Item
from .forms import TypeForm, SubjectForm, LevelForm, PriceForm, ItemForm, ItemFormSet

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

class Cart(View):
    def get(self, request):
        formset = ItemFormSet(queryset=Item.objects.none())
        # form = ItemForm()
        return render(request, "shop/cart.html", {'formset': formset})

    def post(self, request):
        form = ItemForm(data=request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.type = new_item.subject.type
            price = Price.objects.filter(
                type=new_item.type,
                subject=new_item.subject,
                level=new_item.level,
                min_range__lte=new_item.number,
                max_range__gte=new_item.number,
                is_available=True,
            ).first().price
            new_item.item_price = price * new_item.number
            new_item.order = Order.objects.get(id=1)
            new_item.save()
            messages.success(request, 'سفارش شما ایجاد شد.')
        return redirect("shop:pricing")