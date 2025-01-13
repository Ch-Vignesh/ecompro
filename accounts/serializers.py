from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Vendor, Customer



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer  # Directly use the Customer model
        fields = ["email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Use the CustomUserManager's create_user method
        user = Customer.objects.create_user(**validated_data)
        return user
    
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor  # Use the Vendor model directly
        fields = ["email", "business_name", "contact_number", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = Vendor.objects.create_user(**validated_data)  # Use the Vendor manager
        return user 