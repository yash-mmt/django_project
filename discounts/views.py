from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import CouponSerializer , CouponApplySerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import Coupon
# Create your views here.


class CouponAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    @extend_schema(
        request=CouponApplySerializer,  
        responses={200: CouponSerializer}  
    )
    def get(self,request):
        if request.user.is_superuser:
            coupon = Coupon.objects.all()
        else:
            coupon = Coupon.objects.filter(is_active=True)
        
        serializer = CouponSerializer(coupon,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    @extend_schema(
        request=CouponApplySerializer, 
        responses={200: CouponSerializer}
    )
    def patch(self, request, pk):
        coupon = get_object_or_404(Coupon, pk=pk)

        if not request.user.is_superuser:
            return Response({"error": "You are not authorized to update this coupon."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = CouponSerializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CouponSerializer(coupon).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CouponListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    @extend_schema(
        request=CouponApplySerializer,  
        responses={200: CouponSerializer}  
    )

    def post(self,request):
        coupon=CouponSerializer(data=request.data)
        if coupon.is_valid():
            coupon.save()

            return Response(coupon.data,status=status.HTTP_201_CREATED)
        else:
            return Response({"message":coupon.errors},status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
    responses={200: CouponSerializer(many=True)})

    def get(self, request):
        if request.user.is_superuser:
            coupons = Coupon.objects.all()
        else:
            coupons = Coupon.objects.filter(is_active=True)

        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)