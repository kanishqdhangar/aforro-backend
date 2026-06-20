from rest_framework import serializers
from .models import Order

class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity_requested = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    items = OrderItemCreateSerializer(
        many=True
    )


class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField()

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "created_at",
            "total_items",
        ]