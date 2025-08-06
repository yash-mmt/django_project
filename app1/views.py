from rest_framework.views import APIView
from rest_framework import status
from .models import Category, Item , Cart , CartItem ,Address ,Order ,OrderItem
from .serializers import CategorySerializer, ItemSerializer , CartItemSerializer ,AddressSerializer , OrderSerializer
from rest_framework.response import Response    
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.http import FileResponse
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


class ItemAPI(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        items = Item.objects.filter(is_active=True, stock_count__gt=0)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if request.user != item.user and not request.user.is_superuser:
            return Response({'error': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if request.user != item.user and not request.user.is_superuser:
            return Response({'error': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)

        if item.stock_count > 0:
            return Response(
                {'error': 'Product is in stock, cannot delete.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.delete()
        return Response({'message': 'Item deleted successfully.', "stock": item.stock_count}, status=status.HTTP_200_OK)
        
class CategoryAPI(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        items = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(items, many=True)
        return Response(serializer.data)
     
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        item = get_object_or_404(Category, pk=pk, user=request.user)  
        serializer = CategorySerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk, user=request.user)

        if category.items.filter(is_active=True).exists():
            return Response(
                {'error': 'Cannot delete category. It has active items.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        category.delete()
        return Response({'message': 'Category deleted successfully.'}, status=status.HTTP_200_OK)


class CartAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        if request.user.is_superuser:
            cart_items = CartItem.objects.select_related('cart__user', 'item').all()
            data = []
            for cart_item in cart_items:
                serialized_item = CartItemSerializer(cart_item).data
                serialized_item['user'] = {
                    "id": str(cart_item.cart.user.id),
                    "username": cart_item.cart.user.username,
                    "email": cart_item.cart.user.email
                }
                data.append(serialized_item)
            return Response(data, status=status.HTTP_200_OK)

        else:
            cart = self.get_cart(request.user)
            cart_items = cart.cart_items.all()
            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        item_id = request.data.get('item')
        if not item_id:
            return Response({'error': 'Item ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, id=item_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

        if not created:
            if cart_item.quantity + 1 > item.stock_count:
                return Response({'error': 'Cannot add more than stock availability.'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += 1
        else:
            if item.stock_count < 1:
                return Response({'error': 'Item is out of stock.'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = 1

        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk)
        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)

        if serializer.is_valid():
            new_quantity = serializer.validated_data.get('quantity', cart_item.quantity)
            item_stock = cart_item.item.stock_count

            if new_quantity > item_stock:
                return Response({'error': f'Cannot set quantity to {new_quantity}. Only {item_stock} in stock.'},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)
        cart_item.delete()
        return Response({'message': 'Item removed from cart.'}, status=status.HTTP_200_OK)
    

class AddressAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes= [IsAuthenticated]

    def post(self,request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)       
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        address=Address.objects.filter(user=request.user)
        serializer=AddressSerializer(address,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def patch(self,request,pk):
        address = get_object_or_404(Address,pk=pk,user=request.user)
        
        if "is_default" in request.data and request.data["is_default"]:
            Address.objects.filter(user=request.user).update(is_default=False)

        serializer= AddressSerializer(address,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        address = get_object_or_404(Address,pk=pk,user=request.user)
        address.delete()
        return Response({'message': 'Address deleted successfully.'}, status=status.HTTP_200_OK)

class OrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # if request.user.is_superuser:
        #     orders = Order.objects.prefetch_related('order_items__item').all()
        # else:
        #     orders = Order.objects.prefetch_related('order_items__item').filter(user=request.user)

        # data = []

        # for order in orders:
        #     order_data = {
        #         "order_id": order.pk,
        #         "total_bill_amount": order.total_amount,
        #         "user": order.user.username  
        #     }

        #     items = []
        #     for order_item in order.order_items.all():
        #         items.append({
        #             "item": order_item.id,
        #             "name": order_item.item.description,
        #             "rate": order_item.rate,
        #             "quantity": order_item.quantity
        #         })

        #     order_data["items"] = items
        #     data.append(order_data)

        # return Response({"data": data}, status=status.HTTP_200_OK)
        if request.user.is_superuser:
            orders = Order.objects.select_related('user').prefetch_related('order_items__item').all()
        else:
            orders = Order.objects.select_related('user').prefetch_related('order_items__item').filter(user=request.user)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self,request,pk):
        if request.user.is_superuser:
            order=get_object_or_404(Order,pk=pk,user=request.data.get("user_id"))
        else:
            order=get_object_or_404(Order,pk=pk,user=request.user)

        serializer=OrderSerializer(order,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                     

    def post(self, request):
        address_id = request.data.get('address_id')

        if address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            address = Address.objects.filter(user=request.user, is_default=True).first()
            if not address:
                return Response({"error": "No default address found. Please provide an address."},
                                status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.cart_items.select_related('item').all()

        if not cart_items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = 0.0

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                cart=cart,
                address=address,
                total_amount=0,  
                is_paid=False
            )

            for cart_item in cart_items:
                item = cart_item.item
                if item.stock_count < cart_item.quantity:
                    transaction.set_rollback(True)
                    return Response({
                        "error": f"Not enough stock for {item.description}."
                    }, status=status.HTTP_400_BAD_REQUEST)

                item.stock_count -= cart_item.quantity
                item.save()

                line_total = cart_item.quantity * item.rate
                total_amount += line_total

                OrderItem.objects.create(
                    order=order,
                    item=item,
                    quantity=cart_item.quantity,
                    rate=item.rate,
                    line_total=line_total
                )

            order.total_amount = total_amount
            order.save()

            cart_items.delete()

        return Response({
            "message": "Order placed successfully.",
            "order_id": str(order.id)[:8].upper(),
            "total_amount": total_amount
        }, status=status.HTTP_201_CREATED)


class InvoicePDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = order.order_items.select_related('item').all()  

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        short_order_id = str(order.id)[:8].upper()
        elements.append(Paragraph(f"INVOICE - Order #{short_order_id}", styles['Title']))
        elements.append(Spacer(1, 12))

        address = order.address
        address_text = f"{address.address_line}, {address.city}, {address.state}, {address.postal_code}, {address.country}"
        elements.append(Paragraph(f"Customer: {order.user.username}", styles['Normal']))
        elements.append(Paragraph(f"Shipping Address: {address_text}", styles['Normal']))
        elements.append(Paragraph(f"Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"Payment Status: {'PAID' if order.is_paid else 'UNPAID'}", styles['Normal']))
        elements.append(Spacer(1, 12))

        table_data = [["Item Description", "Quantity", "Rate (₹)", "Line Total (₹)"]]

        for order_item in order_items:
            item = order_item.item
            table_data.append([
                item.description,
                str(order_item.quantity),
                f"{order_item.rate:.2f}",
                f"{order_item.line_total:.2f}"
            ])

        table_data.append(["", "", "Grand Total", f"{order.total_amount:.2f}"])

        table = Table(table_data, hAlign='LEFT', colWidths=[200, 80, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)

        buffer.seek(0)
        filename = f"Invoice_{short_order_id}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)