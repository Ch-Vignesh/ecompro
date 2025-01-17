# catalog/views.py
from accounts.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from .models import Product, Attribute, Value, ProductAttribute, Variant, VariantImage, Review, Reply, Category
from .serializers import (

    AttributeSerializer,
    ValueSerializer,
    ProductAttributeSerializer,
    ProductDetailSerializer,
    VariantSerializer,
    ReviewSerializer,
    ReplySerializer,
    CategorySerializer,
    VariantImageSerializer
)
from rest_framework.pagination import PageNumberPagination
import uuid
from rest_framework.permissions import IsAuthenticated
from .permissions import IsVendor
from rest_framework_simplejwt.authentication import JWTAuthentication

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10 # Default page size, you can change it to any value
    page_size_query_param = 'page_size'  # Allow clients to specify the page size
    page_query_param = 'page'  # Allow clients to specify the page number
    max_page_size = 100  # Maximum page size allowed



class CategoryCreateView(APIView):

    def get(self, request):
        category_id = request.query_params.get('c_id', None)

        if category_id:
            # Fetch a specific category by category_id
            try:
                category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Get all products for this specific category
            products = Product.objects.filter(category=category)
            serializer = ProductDetailSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Fetch all categories if category_id is not provided
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request):
        """Create a new category."""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# View to handle Product creation and listing
class ProductView(APIView):
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Dynamically assign permissions based on the request method.
        - Allow unauthenticated access for 'GET'.
        - Require authentication for 'POST'.
        """
        if self.request.method == "GET":
            return []  # No authentication required for GET
        return [IsAuthenticated()]

    def get(self, request):
        # Check if the user is authenticated
        user = request.user if request.user.is_authenticated else None

        if user:
            try:
                # Check if the user is a vendor
                vendor = Vendors.objects.get(email=user.email)
                # Filter products by the vendor
                products = Product.objects.filter(seller=vendor.email)
            except Vendors.DoesNotExist:
                # If the user is authenticated but not a vendor, return all products
                products = Product.objects.all()
        else:
            # If the user is not authenticated, return all products
            products = Product.objects.all()

        # Apply pagination
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(products, request)

        # Serialize the products
        serializer = ProductDetailSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        # Ensure that only a vendor can add products
        user = request.user

        # Check if the user is a vendor by looking for the related 'Vendors' instance
        try:
            vendor = Vendors.objects.get(email=user.email)
        except Vendors.DoesNotExist:
            return Response({"detail": "You must be a vendor to add products."}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the product data from the request
        serializer = ProductDetailSerializer(data=request.data)

        if serializer.is_valid():
            # Save the product and associate the vendor as the seller
            product = serializer.save(seller=vendor.email)  # Save the vendor's email as the seller
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to handle Attribute creation
class AttributeView(APIView):
    def get(self, request):
        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AttributeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to handle Value creation
class ValueView(APIView):
    def get(self, request):
        values = Value.objects.all()
        serializer = ValueSerializer(values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ValueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to handle ProductAttribute creation
class ProductAttributeView(APIView):

    def get(self, request):
        product_attributes = ProductAttribute.objects.all()
        serializer = ProductAttributeSerializer(product_attributes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductAttributeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to fetch all products with detailed attributes and values
class ProductDetailsView(APIView):
    # Fetch details of a specific product
    def get(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not  found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request, pk):
        
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product   not found."}, status=status.HTTP_404_NOT_FOUND)

        attribute_name = request.data.get("attribute")
        value_name = request.data.get("value")

        if not attribute_name or not value_name:
            return Response(
                {"error": "Both 'attribute' and 'value' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create the attribute
        attribute, _ = Attribute.objects.get_or_create(name=attribute_name)

        # Get or create the value for the attribute
        value, _ = Value.objects.get_or_create(attribute=attribute, value=value_name)

        # Link the product with the attribute and value
        _product_attribute, created = ProductAttribute.objects.get_or_create(
            product=product, attribute=attribute, value=value
        )

        if created:
            return Response(
                {"message": "Attribute and value added to product."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "Attribute and value already exist for this product."},
            status=status.HTTP_200_OK,
        )




class ValuesByAttributeView(APIView):

    def get(self, request, attribute_id):
        try:
            # Ensure the attribute exists
            attribute = Attribute.objects.get(pk=attribute_id)
        except Attribute.DoesNotExist:
            return Response({"error": "Attribute not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch all values associated with the attribute
        values = Value.objects.filter(attribute=attribute)
        serializer = ValueSerializer(values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class SearchView(APIView):

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        brand = request.query_params.get("brand", "").strip()

        if not query and not brand:
            return Response(
                {"error": "Please provide a search query using the '?q=' for parameter & '?brand' for brand"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Start with all products, but filter if the user is a vendor
        if hasattr(request, 'user') and isinstance(request.user, Vendors):
            # If the user is a vendor, only allow them to search their own products
            products = Product.objects.filter(vendor=request.user)
        else:
            # If the user is a customer or not authenticated, allow them to search all products
            products = Product.objects.all()

        # Filter products by query
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        # Filter products by brand
        if brand:
            products = products.filter(brand__icontains=brand)

        # Serialize and return the filtered products
        product_serializer = ProductDetailSerializer(products, many=True)
        
        variants = Variant.objects.filter(product__in=products).select_related("product")
        variant_serializer = VariantSerializer(variants, many=True)
        
        return Response(
            {   
                "products": product_serializer.data,
                "variants": variant_serializer.data,
            },
            status=status.HTTP_200_OK
        )




class VariantImageUploadView(APIView):
    
    def post(self, request, variant_id):
        try:
            variant = Variant.objects.get(id=variant_id)
        except Variant.DoesNotExist:
            return Response({"error": "Variant not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the current authenticated user
        user = request.user

        try:
            # Check if the user is a vendor
            vendor = Vendors.objects.get(email=user.email)
        except Vendors.DoesNotExist:
            return Response({"error": "You must be a vendor to upload images."}, status=status.HTTP_403_FORBIDDEN)

        # Ensure the vendor is the one associated with the product (seller field)
        if variant.product.seller != vendor.email:
            return Response({"error": "You are not authorized to upload images for this variant."}, status=status.HTTP_403_FORBIDDEN)

        uploaded_images = request.FILES.getlist('images')
        is_main_image_flag = request.data.get('is_main_image', 'false').lower() == 'true'

        for index, image in enumerate(uploaded_images):
            is_main_image = is_main_image_flag if index == 0 else False
            variant_image = VariantImage.objects.create(
                variant=variant, image=image, is_main_image=is_main_image
            )

            # Update the product's image if this is the first image
            if index == 0 and not variant.product.image:
                variant.product.image = variant_image.image
                variant.product.save()

        return Response({"message": "Images uploaded successfully."}, status=status.HTTP_201_CREATED)

class VariantView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        # Ensure the logged-in user is a vendor
        user = request.user
        try:
            vendor = Vendors.objects.get(email=user.email)
        except Vendors.DoesNotExist:
            return Response({"error": "You must be a vendor to add variants."}, status=status.HTTP_403_FORBIDDEN)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the product belongs to the logged-in vendor
        if product.seller != vendor.email:
            return Response({"error": "You can only add variants to your own products."}, status=status.HTTP_403_FORBIDDEN)

        # Process the variant attributes, SKU, price, and stock
        attribute_values = request.data.get("attributes", [])
        sku = request.data.get("sku", None)
        price = request.data.get("price", None)
        stock = request.data.get("stock", 0)

        # Auto-generate SKU if not provided
        if not sku:
            sku = f"{product.name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:6]}"

        # Ensure SKU is unique
        if Variant.objects.filter(sku=sku).exists():
            return Response({"error": "SKU already exists. Please provide a unique SKU."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure attribute values are provided
        if not attribute_values:
            return Response({"error": "Attributes are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the values for the attributes and map them to the correct attribute names
        attributes_to_save = []
        for attribute_value in attribute_values:
            attribute_name = attribute_value.get("attribute")
            value_name = attribute_value.get("value")

            if not attribute_name or not value_name:
                return Response({"error": "Each attribute must have a name and value."}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create the attribute
            attribute, _ = Attribute.objects.get_or_create(name=attribute_name)

            # Get or create the value for the attribute
            value, _ = Value.objects.get_or_create(attribute=attribute, value=value_name)

            # Append the value to the list of attributes to be associated with the variant
            attributes_to_save.append(value)

        # Create the variant and associate it with the product and vendor
        variant = Variant.objects.create(product=product, sku=sku, price=price, stock=stock)
        variant.attributes.set(attributes_to_save)  # Assign the values to the variant
        variant.save()

        # Serialize and return the created variant
        serializer = VariantSerializer(variant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, product_id):
        # Ensure the logged-in user is a vendor
        user = request.user
        try:
            vendor = Vendors.objects.get(email=user.email)
        except Vendors.DoesNotExist:
            return Response({"error": "You must be a vendor to view variants."}, status=status.HTTP_403_FORBIDDEN)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the product belongs to the logged-in vendor
        if product.seller != vendor.email:
            return Response({"error": "You can only view variants for your own products."}, status=status.HTTP_403_FORBIDDEN)

        # Get variants for the product
        variants = Variant.objects.filter(product=product)

        # Serialize and return the variants
        serializer = VariantSerializer(variants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, product_id):
        # Ensure the logged-in user is a vendor
        user = request.user
        try:
            vendor = Vendors.objects.get(email=user.email)
        except Vendors.DoesNotExist:
            return Response({"error": "You must be a vendor to update variants."}, status=status.HTTP_403_FORBIDDEN)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the product belongs to the logged-in vendor
        if product.seller != vendor.email:
            return Response({"error": "You can only update variants for your own products."}, status=status.HTTP_403_FORBIDDEN)

        variant_id = request.data.get("variant_id", None)
        if not variant_id:
            return Response({"error": "Variant ID is required for updates."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            variant = Variant.objects.get(pk=variant_id, product=product)
        except Variant.DoesNotExist:
            return Response({"error": "Variant not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update attributes if provided
        attribute_values = request.data.get("attributes", [])
        if attribute_values:
            attributes_to_save = []
            for attribute_value in attribute_values:
                attribute_name = attribute_value.get("attribute")
                value_name = attribute_value.get("value")

                if not attribute_name or not value_name:
                    return Response({"error": "Each attribute must have a name and value."}, status=status.HTTP_400_BAD_REQUEST)

                attribute, _ = Attribute.objects.get_or_create(name=attribute_name)
                value, _ = Value.objects.get_or_create(attribute=attribute, value=value_name)
                attributes_to_save.append(value)

            variant.attributes.set(attributes_to_save)

        # Update SKU, price, and stock if provided
        sku = request.data.get("sku", None)
        price = request.data.get("price", None)
        stock = request.data.get("stock", None)

        if sku:
            if Variant.objects.filter(sku=sku).exclude(pk=variant_id).exists():
                return Response({"error": "SKU already exists. Please provide a unique SKU."}, status=status.HTTP_400_BAD_REQUEST)
            variant.sku = sku

        if price:
            variant.price = price

        if stock is not None:
            variant.stock = stock

        variant.save()

        serializer = VariantSerializer(variant)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ReviewView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the user is a vendor and owns the product
        user = request.user
        try:
            vendor = Vendors.objects.get(email=user.email)
            if product.seller != vendor.email:
                return Response({"error": "You can only view reviews for your own products."}, status=status.HTTP_403_FORBIDDEN)
        except Vendors.DoesNotExist:
            return Response({"error": "You must be a vendor to view reviews for this product."}, status=status.HTTP_403_FORBIDDEN)

        # Get reviews for the product
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, product_id):
        # Ensure the user is a customer
        user = request.user
        try:
            Customers.objects.get(email=user.email)
        except Customers.DoesNotExist:
            return Response({"error": "Only customers can add reviews."}, status=status.HTTP_403_FORBIDDEN)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ReplyView(APIView):
    def get(self, request, review_id):
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        # If the user is a vendor, ensure they are allowed to see replies for their product only
        if isinstance(request.user, Vendors):
            # Vendor can only see replies for their own products
            if review.product.seller != request.user.email:
                return Response({"error": "You can only view replies for your own products."}, status=status.HTTP_403_FORBIDDEN)
            else :
                print("your products")

        else:
        # Customers can see all replies
            replies = Reply.objects.filter(review=review)
            serializer = ReplySerializer(replies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, review_id):
        # Ensure the user is a vendor (only vendors can post replies)
        if not isinstance(request.user, Vendors):
            return Response({"error": "Only vendors can post replies."}, status=status.HTTP_403_FORBIDDEN)

        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the review belongs to the product the vendor is selling
        if review.product.seller != request.user.email:
            return Response({"error": "You can only reply to reviews on products you are selling."}, status=status.HTTP_403_FORBIDDEN)

        # Serialize and save the reply
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(review=review, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VariantPriceRangeView(APIView):
    def get(self, request, category_id):
        # Get the price range from query parameters
        min_price = request.query_params.get("min_price", None)
        max_price = request.query_params.get("max_price", None)

        # Check if both min_price and max_price are provided
        if min_price is None or max_price is None:
            return Response(
                {"error": "Both 'min_price' and 'max_price' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        # Filter products in the given category
        products = Product.objects.filter(category=category)

        # Fetch variants within the given price range
        variants = Variant.objects.filter(product__in=products, price__gte=min_price, price__lte=max_price)

        # Serialize the variants
        serializer = VariantSerializer(variants, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
