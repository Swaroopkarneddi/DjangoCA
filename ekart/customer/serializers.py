from rest_framework import serializers
from .models import UserCustomer

class UserCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustomer
        fields = ['id', 'name', 'email', 'address', 'phone']
