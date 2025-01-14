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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customer, Vendor
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customer, Vendor


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if email and password are provided
        if not email or not password:
            return Response({'msg': 'Email and Password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to find the user in both Customer and Vendor models
        user = None
        try:
            user = Customer.objects.get(email=email)
            user_type = "Customer"
        except Customer.DoesNotExist:
            try:
                user = Vendor.objects.get(email=email)
                user_type = "Vendor"
            except Vendor.DoesNotExist:
                return Response({'msg': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Log the user and password for debugging purposes
        print(f"User found in {user_type} model:", user)
        print(f"Password provided: {password}")
        print(f"Stored password (hashed): {user.password}")

        # Check password: ensure the password is not hashed here; it's plaintext
        if user and user.check_password(password):
            print(f"Password check success for {user.email}")
            # Password is correct, check if the user is active
            if not user.is_active:
                return Response({'msg': 'User is inactive'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
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
from .models import Customer, Vendor
from .serializers import CustomerSerializer, VendorSerializer



# View for listing all customers
class CustomerListView(ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# View for listing all vendors
class VendorListView(ListAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer



from rest_framework.generics import RetrieveAPIView

# View for retrieving a specific customer by ID
class CustomerDetailView(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# View for retrieving a specific vendor by ID
class VendorDetailView(RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer




from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

# View for updating a specific customer's details
class CustomerUpdateView(UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
   # permission_classes = [IsAuthenticated]  # Optional: Restrict updates to authenticated users only

# View for updating a specific vendor's details
class VendorUpdateView(UpdateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    #permission_classes = [IsAuthenticated]  # Optional: Restrict updates to authenticated users only

