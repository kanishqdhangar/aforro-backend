from rest_framework import serializers
from .models import Inventory


class InventoryListSerializer(
    serializers.ModelSerializer
):

    title = serializers.CharField(
        source="product.title"
    )

    price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    category = serializers.CharField(
        source="product.category.name"
    )

    class Meta:
        model = Inventory

        fields = [
            "title",
            "price",
            "category",
            "quantity",
        ]