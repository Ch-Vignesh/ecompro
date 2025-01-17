from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Vendors, Customers



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers  # Directly use the Customers model
        fields = ["id","email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Use the CustomUserManager's create_user method
        user = Customers.objects.create_user(**validated_data)
        return user
    
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors  # Use the Vendors model directly
        fields = ["id","email", "business_name", "contact_number", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = Vendors.objects.create_user(**validated_data)  # Use the Vendor manager
        return user 