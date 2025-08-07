from rest_framework import serializers
from .models import Coupon , CouponUsage
from django.utils import timezone


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["id","code","discount_percent","valid_from","valid_to","usage_limit","usage_count","is_active"] 
    
    def validate(self, data):
        valid_from = data.get("valid_from")
        valid_to = data.get("valid_to")

        if valid_from and valid_to and valid_from > valid_to:
            raise serializers.ValidationError({
                "valid_to": "valid_to must be after or equal to valid_from."
            })

        code = data.get("code")
        now = timezone.now()

        if code:
            existing_coupons = Coupon.objects.filter(code=code).order_by('-created_at')
            for coupon in existing_coupons:
                if coupon.is_active and coupon.valid_to >= now:
                    if coupon.usage_limit == 0 or coupon.usage_count < coupon.usage_limit:
                        raise serializers.ValidationError({
                            "code": "An active, valid, and unused coupon with this code already exists."
                        })

        return data
class CouponApplySerializer(serializers.Serializer):
    coupon_code = serializers.CharField()

    def validate_coupon_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")

        if not coupon.is_valid():
            raise serializers.ValidationError("Coupon is not valid or expired.")

        user = self.context['request'].user
        if CouponUsage.objects.filter(user=user, coupon=coupon).exists():
            raise serializers.ValidationError("You have already used this coupon.")

        return value

    def validate(self, data):
        coupon = Coupon.objects.get(code=data['coupon_code'])
        data['coupon'] = coupon
        return data

class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField()