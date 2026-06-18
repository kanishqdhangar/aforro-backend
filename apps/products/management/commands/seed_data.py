import random

from django.core.management.base import BaseCommand
from faker import Faker

from apps.products.models import Category, Product
from apps.stores.models import Store, Inventory


class Command(BaseCommand):
    help = "Generate demo data"

    def handle(self, *args, **kwargs):
        fake = Faker()

        self.stdout.write("Creating categories...")

        categories = []

        category_names = [
            "Electronics",
            "Fashion",
            "Books",
            "Sports",
            "Beauty",
            "Furniture",
            "Toys",
            "Groceries",
            "Automotive",
            "Health",
            "Music",
            "Gaming",
        ]

        for name in category_names:
            category, _ = Category.objects.get_or_create(
                name=name
            )
            categories.append(category)

        self.stdout.write("Creating products...")

        products = []

        for i in range(1000):
            product = Product.objects.create(
                title=fake.unique.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                price=round(random.uniform(10, 5000), 2),
                category=random.choice(categories),
            )

            products.append(product)

        self.stdout.write("Creating stores...")

        stores = []

        for i in range(20):
            store = Store.objects.create(
                name=f"Store {i+1}",
                location=fake.city(),
            )

            stores.append(store)

        self.stdout.write("Creating inventory...")

        inventory_rows = []

        for store in stores:
            selected_products = random.sample(
                products,
                300
            )

            for product in selected_products:
                inventory_rows.append(
                    Inventory(
                        store=store,
                        product=product,
                        quantity=random.randint(1, 100),
                    )
                )

        Inventory.objects.bulk_create(
            inventory_rows,
            batch_size=1000
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed data created successfully."
            )
        )