from rest_framework import serializers
from .models import Category, Item , Cart ,CartItem , Address

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True,read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name" , "is_active" , "items"]

class CartItemSerializer(serializers.ModelSerializer):
    item_details = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'item', 'quantity', 'item_details']

    def validate(self, data):
        item = data.get('item')
        quantity = data.get('quantity')

        if item and quantity:
            if quantity > item.stock_count:
                raise serializers.ValidationError(f"Cannot add {quantity} items. Only {item.stock_count} in stock.")
        return data

    def get_item_details(self, obj):
        return {
            "description": obj.item.description,
            "rate": obj.item.rate,
            "stock_count": obj.item.stock_count
        }
class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ['id', 'user', 'created_at']

        