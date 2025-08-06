from django.urls import path
from .views import CouponAPIView,CouponListCreateAPIView

urlpatterns = [
    path('coupon/', CouponListCreateAPIView.as_view(), name='get-add-coupon'),
    path('coupon/<uuid:pk>/', CouponAPIView.as_view(), name='update-delete'),
    ]