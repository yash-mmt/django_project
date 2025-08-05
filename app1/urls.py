from django.urls import path
from .views import ItemAPI , CategoryAPI , CartAPIView , OrderAPIView ,AddressAPIView ,InvoicePDFAPIView

urlpatterns = [
    path('items/', ItemAPI.as_view(), name='item-list-create'),
    path('items/<uuid:pk>/', ItemAPI.as_view(), name='item-update'),
    path('categoryAPI/', CategoryAPI.as_view(), name='item-list-create'),
    path('categoryAPI/<uuid:pk>/', CategoryAPI.as_view(), name='CategoryAPI-update'),
    path('cart/', CartAPIView.as_view(), name='cart-add'),
    path('cart/items/<uuid:pk>/', CartAPIView.as_view(), name='cart-item-detail'),
    path('order/',OrderAPIView.as_view(),name="order"),
    path("address/",AddressAPIView.as_view(),name="address"),
    path("address/<uuid:pk>/",AddressAPIView.as_view(),name="address_update"),
    path('order/<uuid:order_id>/invoice/', InvoicePDFAPIView.as_view(), name='invoice-pdf'),
    ]