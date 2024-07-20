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

    def get(self, request):
        return render(request, "shop/pricing.html", self.context)
    
    def post(self, request):
        if 'type_form' in request.POST:
            form = TypeForm(request.POST)
            if form.is_valid():
                form.save()
            return render(request, "shop/pricing.html", self.context)
        
        elif 'level_form' in request.POST:
            form = LevelForm(request.POST)
            if form.is_valid():
                form.save()
            return render(request, "shop/pricing.html", self.context)
        
        elif 'subject_form' in request.POST:
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
            return render(request, "shop/pricing.html", self.context)

        elif 'price_form' in request.POST:
            form = PriceForm(request.POST)
            if form.is_valid():
                form.save()
            return render(request, "shop/pricing.html", self.context)
        
