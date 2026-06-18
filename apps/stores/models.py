from django.db import models
from apps.products.models import Product


class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return self.name


class Inventory(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="inventory"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory"
    )

    quantity = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["store", "product"],
                name="unique_store_product_inventory"
            )
        ]

        indexes = [
            models.Index(fields=["store"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.store.name} - {self.product.name}"