from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomerSerializer, VendorSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication




class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'msg': 'Customer registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class RegisterVendorView(APIView):
    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'msg': 'Vendor registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView



from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customers, Vendors
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customers, Vendors


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customers, Vendors
from django.contrib.auth import get_user_model

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if email and password are provided
        if not email or not password:
            return Response({'msg': 'Email and Password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to find the user in Customer, Vendor, or Superuser models
        user = None
        user_type = None

        # Check for Customer
        try:
            user = Customers.objects.get(email=email)
            user_type = "Customer"
        except Customers.DoesNotExist:
            pass
        
        # Check for Vendor
        if not user:
            try:
                user = Vendors.objects.get(email=email)
                user_type = "Vendor"
            except Vendors.DoesNotExist:
                pass
        
        # Check for Superuser (using custom user model)
        if not user:
            try:
                user = get_user_model().objects.get(email=email)  # Custom user model
                # if user.is_superuser:  # Check if the user is a superuser
                #     user_type = "Superuser"
                # else:
                #     user = None  # If not a superuser, set user to None
            except get_user_model().DoesNotExist:
                pass

        # If no user is found, return error
        if not user:
            return Response({'msg': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if password is correct
        if user.check_password(password):
            # Password is correct, check if the user is active
            if not user.is_active:
                return Response({'msg': 'User is inactive'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            print(user.is_authenticated)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        # If password is incorrect
        return Response({'msg': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        # You can instruct the client to discard the token (by just returning a message)
        return Response({"msg": "Successfully logged out"}, status=200)
    


from rest_framework.generics import ListAPIView
from .models import Customers, Vendors
from .serializers import CustomerSerializer, VendorSerializer



# View for listing all customers
class CustomerListView(ListAPIView):
    queryset = Customers.objects.all()
    serializer_class = CustomerSerializer


# View for listing all vendors
class VendorListView(ListAPIView):
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer



from rest_framework.generics import RetrieveAPIView

# View for retrieving a specific customer by ID
class CustomerDetailView(RetrieveAPIView):
    queryset = Customers.objects.all()
    serializer_class = CustomerSerializer


# View for retrieving a specific vendor by ID
class VendorDetailView(RetrieveAPIView):
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer




from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

# View for updating a specific customer's details
class CustomerUpdateView(UpdateAPIView):
    queryset = Customers.objects.all()
    serializer_class = CustomerSerializer
   # permission_classes = [IsAuthenticated]  # Optional: Restrict updates to authenticated users only

# View for updating a specific vendor's details
class VendorUpdateView(UpdateAPIView):
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer
    #permission_classes = [IsAuthenticated]  # Optional: Restrict updates to authenticated users only




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Customers, Vendors
from .serializers import CustomerSerializer, VendorSerializer

# Admin-only permission
class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

# Admin: List all customers
class AdminCustomerListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        customers = Customers.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Admin: List all vendors
class AdminVendorListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        vendors = Vendors.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Admin: Manage a specific customer (Retrieve, Update, Delete)
class AdminCustomerDetailView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, pk):
        try:
            customer = Customers.objects.get(pk=pk)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            customer = Customers.objects.get(pk=pk)
            serializer = CustomerSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            customer = Customers.objects.get(pk=pk)
            customer.delete()
            return Response({"msg": "Customer deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)


# Admin: Manage a specific vendor (Retrieve, Update, Delete)
class AdminVendorDetailView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, pk):
        try:
            vendor = Vendors.objects.get(pk=pk)
            serializer = VendorSerializer(vendor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Vendors.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            vendor = Vendors.objects.get(pk=pk)
            serializer = VendorSerializer(vendor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Vendors.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            vendor = Vendors.objects.get(pk=pk)
            vendor.delete()
            return Response({"msg": "Vendor deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Vendors.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)


