from django.shortcuts import render
from django.views import View

from .models import Price
from .forms import TypeForm, SubjectForm, LevelForm, PriceForm

class Pricing(View):
    forms = {
            'type_form': TypeForm(),
            'level_form': LevelForm(),
            'subject_form': SubjectForm(),
            'price_form': PriceForm()
        }
    prices = Price.objects.all().order_by('type__type')
    context = {
        'forms': forms,
        'prices': prices,
        }
    
    def invalid_form(self, request, form_name: str, form):
        """ The specific form will be populated with the data previously submitted. """
        context = self.context
        context['forms'][form_name] = form
        return render(request, "shop/pricing.html", context)

    def get(self, request):
        return render(request, "shop/pricing.html", self.context)
    
    def post(self, request):
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
                form.save()
                return render(request, "shop/pricing.html", self.context)
            return self.invalid_form(request, 'price_form', form)
        
