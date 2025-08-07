from django.utils import timezone
from rest_framework.response import Response
from .models import Coupon
from rest_framework import status

def validate_code(coupon):
    
    if not coupon:
        return False, "Invalid Coupon Code."

    now = timezone.now()
    if coupon.valid_to < now:
        return False, "Coupon has expired."

    if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
        return False, "Coupon usage limit reached."

    return True,0