from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import (
    Category,
    Product,
)

from apps.stores.models import (
    Store,
    Inventory,
)

from apps.orders.models import Order


class CreateOrderAPITest(APITestCase):

    def setUp(self):

        self.category = Category.objects.create(
            name="Electronics"
        )

        self.product = Product.objects.create(
            category=self.category,
            title="Gaming Laptop",
            description="Test laptop",
            price=1000,
        )

        self.store = Store.objects.create(
            name="Store 1",
            location="Delhi",
        )

    def test_order_confirmed(self):

        Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=20,
        )

        payload = {
            "store_id": self.store.id,
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity_requested": 5,
                }
            ],
        }

        response = self.client.post(
            "/orders/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(
            id=response.data["order_id"]
        )

        self.assertEqual(
            order.status,
            "CONFIRMED",
        )

        inventory = Inventory.objects.get(
            store=self.store,
            product=self.product,
        )

        self.assertEqual(
            inventory.quantity,
            15,
        )

    def test_order_rejected(self):

        Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=2,
        )

        payload = {
            "store_id": self.store.id,
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity_requested": 5,
                }
            ],
        }

        response = self.client.post(
            "/orders/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(
            id=response.data["order_id"]
        )

        self.assertEqual(
            order.status,
            "REJECTED",
        )

        inventory = Inventory.objects.get(
            store=self.store,
            product=self.product,
        )

        self.assertEqual(
            inventory.quantity,
            2,
        )