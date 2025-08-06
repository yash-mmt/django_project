from rest_framework import serializers
from .models import Coupon , CouponUsage


class CouponSerializer(serializers.ModelSerializer):
   
   class Meta:
      model = Coupon
      fields = ["id","code","discount_percent","valid_from","valid_to","usage_limit","usage_count","is_active"] 


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