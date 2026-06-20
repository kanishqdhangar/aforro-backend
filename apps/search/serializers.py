from rest_framework import serializers
from apps.products.models import Product


class ProductSearchSerializer(serializers.ModelSerializer):

    category = serializers.CharField(
        source="category.name"
    )

    available_quantity = serializers.IntegerField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "category",
            "available_quantity",
        ]