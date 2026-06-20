from django.core.cache import cache

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


class ProductSearchAPITest(APITestCase):

    def setUp(self):

        cache.clear()

        self.category = Category.objects.create(
            name="Electronics"
        )

        self.product = Product.objects.create(
            category=self.category,
            title="Gaming Laptop",
            description="Gaming laptop",
            price=1000,
        )

        self.store = Store.objects.create(
            name="Store 1",
            location="Delhi",
        )

        Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=25,
        )

    def test_search_products(self):

        response = self.client.get(
            "/api/search/products/?q=laptop"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "results",
            response.data
        )

        self.assertGreater(
            len(response.data["results"]),
            0,
        )

    def test_search_cache_created(self):

        self.client.get(
            "/api/search/products/?q=laptop"
        )

        cache_key = (
            "product_search:"
            "/api/search/products/?q=laptop"
        )

        self.assertIsNotNone(
            cache.get(cache_key)
        )

    def test_in_stock_filter(self):

        response = self.client.get(
            "/api/search/products/?in_stock=true"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )


class ProductSuggestAPITest(APITestCase):

    def setUp(self):

        cache.clear()

        category = Category.objects.create(
            name="Electronics"
        )

        Product.objects.create(
            category=category,
            title="Gaming Laptop",
            description="Laptop",
            price=1000,
        )

    def test_suggest_endpoint(self):

        response = self.client.get(
            "/api/search/suggest/?q=lap"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "results",
            response.data,
        )

    def test_rate_limit(self):

        response = None

        for _ in range(21):

            response = self.client.get(
                "/api/search/suggest/?q=lap"
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )