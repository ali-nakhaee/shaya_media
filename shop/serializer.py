from rest_framework import serializers
from .models import Price

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['type', 'subject', 'level', 'min_range', 'max_range', 'price', 'is_available', 'discount']
        