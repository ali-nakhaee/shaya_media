from django.shortcuts import render
from django.views import View
from django.http import Http404

from .models import Price
from .forms import TypeForm, SubjectForm, LevelForm, PriceForm

class Pricing(View):

    def make_context(self):
        """ To update context for get and post methods. """
        forms = {
                'type_form': TypeForm(),
                'level_form': LevelForm(),
                'subject_form': SubjectForm(),
                'price_form': PriceForm(),
            }
        prices = Price.objects.all().order_by('type__type').order_by('subject__subject').order_by('level__level_num')
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
        



