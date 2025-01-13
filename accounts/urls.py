from django.urls import path
from .views import RegisterCustomerView, RegisterVendorView, LoginView, LogoutView,  CustomerListView,VendorListView,  CustomerDetailView,VendorDetailView,  CustomerUpdateView, VendorUpdateView

urlpatterns = [
    path('register/customer/', RegisterCustomerView.as_view(), name='register_customer'),
    path('register/vendor/', RegisterVendorView.as_view(), name='register_vendor'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),  # Add this line
    path("customers/", CustomerListView.as_view(), name="customer_list"),
    path("vendors/", VendorListView.as_view(), name="vendor_list"),
    path("customers/<int:pk>/", CustomerDetailView.as_view(), name="customer_detail"),
    path("vendors/<int:pk>/", VendorDetailView.as_view(), name="vendor_detail"),
    path("customers/<int:pk>/update/", CustomerUpdateView.as_view(), name="customer_update"),
    path("vendors/<int:pk>/update/", VendorUpdateView.as_view(), name="vendor_update"),

]
