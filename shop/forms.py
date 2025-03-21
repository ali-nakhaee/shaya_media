""" shop.forms """

from django import forms

from users.models import User
from .models import Type, Subject, Level, Price, Item, Order

class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = ('type', 'unit')
        labels = {
            'type': 'نوع',
            'unit': 'واحد شمارش',
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('type', 'subject')
        labels = {
            'type': 'نوع',
            'subject': 'موضوع',
        }

class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = ('level_num', 'title')
        labels = {
            'level_num': 'رتبه (عدد)',
            'title': 'عنوان',
        }

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ('subject', 'level', 'min_range', 'max_range', 'price', 'is_available', 'discount',)
        labels = {
            'subject': 'موضوع',
            'level': 'سطح',
            'min_range': 'شروع محدوده',
            'max_range': 'پایان محدوده',
            'price': 'قیمت',
            'is_available': 'قابل سفارش',
            'discount': 'تخفیف',
        }


ItemFormSet = forms.modelformset_factory(Item,
                                         fields=('subject', 'level', 'number'),
                                         extra=1,
                                         widgets={
                                             'subject': forms.Select(attrs={'required': 'required'}),
                                             'level': forms.Select(attrs={'required': 'required'}),
                                             'number': forms.NumberInput(attrs={'required': 'required'}),
                                             },
                                         labels={
                                             'subject': 'نوع - موضوع',
                                             'level': 'سطح',
                                             'number': 'تعداد',
                                         }
                                        )
                                          

class ItemForm(forms.Form):
    type = forms.ModelChoiceField(queryset=Type.objects.filter(is_available=True),
                                  label='نوع',
                                  widget=forms.Select(attrs={'class': 'form-select',
                                                             'required': 'required',
                                                             }),
                                  )
    subject = forms.CharField(label='موضوع',
                              widget=forms.Select(attrs={"disabled":"disabled",
                                                         'class': 'form-select',
                                                         'required': 'required',
                                                         }),
                              )
    level = forms.ModelChoiceField(queryset=Level.objects.filter(is_available=True),
                                   label='سطح',
                                   widget=forms.Select(attrs={'class': 'form-select',
                                                              'required': 'required',
                                                              }),
                                   )
    number = forms.IntegerField(help_text=' ',
                                label='مقدار',
                                widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                'required': 'required',
                                                                }),
                                )
    

class OrderStatusForm(forms.Form):
    order_id = forms.IntegerField(widget=forms.HiddenInput())
    status = forms.ChoiceField(choices=Order.STATUS_CHOICES,
                               label='وضعیت',
                               )


class CustomerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.phone_number} - {obj.get_full_name()} - {obj.admin_description}"

class SelectCustomerForm(forms.Form):
    customer = CustomerChoiceField(queryset=User.objects.all(),
                                      label="انتخاب مشتری",
                                      )

