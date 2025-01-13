# catalog/urls.py
from django.urls import path, include
from .views import (
    ProductView,
    AttributeView,
    ValueView,
    ProductAttributeView,
    ProductDetailsView,
    ValuesByAttributeView,
    SearchView,
    VariantView,
    ReplyView,
    ReviewView,
    CategoryCreateView,
    VariantImageUploadView,
    VariantPriceRangeView,
)

urlpatterns = [
 
    path('products/', ProductView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='product-details'),
    path('attributes/', AttributeView.as_view(), name='attribute-list-create'),
    path('values/', ValueView.as_view(), name='value-list-create'),
    path('products-attributes/', ProductAttributeView.as_view(), name='product-attribute-list-create'),
    path('attributes/<int:attribute_id>/values/', ValuesByAttributeView.as_view(), name='values-by-attribute'),
    path('search/', SearchView.as_view(), name='search'),
    path('products/<int:product_id>/variants/', VariantView.as_view(), name='variant-view'),
    path('products/<int:product_id>/reviews/', ReviewView.as_view(), name='product-reviews'),
    path('reviews/<int:review_id>/replies/', ReplyView.as_view(), name='review-replies'),
    path('variants/<int:variant_id>/images/', VariantImageUploadView.as_view(), name='variant-image-upload'),
    path('categories/<int:category_id>/price-range/', VariantPriceRangeView.as_view(), name='variant-price-range'),
    path('categories/', CategoryCreateView.as_view(), name='category-list-create'),
    
    ]
