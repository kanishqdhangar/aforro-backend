from django.db import transaction
from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import (
    Order,
    OrderItem,
)

from apps.orders.serializers import (
    OrderCreateSerializer, OrderListSerializer
)

from apps.stores.models import (
    Store,
    Inventory,
)

from apps.products.models import Product

from .tasks import send_low_stock_alert

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
@extend_schema(
    summary="Create Order",
    description="Create a new order for a store.",
    request=OrderCreateSerializer,
    responses={
        201: inline_serializer(
            name="OrderCreateResponse",
            fields={
                "order_id": serializers.IntegerField(),
                "status": serializers.CharField(),
            },
        )
    },
)
class CreateOrderAPIView(APIView):

    @transaction.atomic
    def post(self, request):

        serializer = OrderCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        store_id = serializer.validated_data["store_id"]
        items = serializer.validated_data["items"]

        store = Store.objects.get(
            id=store_id
        )

        order = Order.objects.create(
            store=store,
            status="PENDING"
        )

        product_ids = [
            item["product_id"]
            for item in items
        ]

        # Lock inventory rows
        inventory_rows = (
            Inventory.objects
            .select_for_update()
            .select_related("product")
            .filter(
                store=store,
                product_id__in=product_ids
            )
        )

        inventory_map = {
            inv.product_id: inv
            for inv in inventory_rows
        }

        has_insufficient_stock = False

        for item in items:

            product_id = item["product_id"]
            requested_qty = item[
                "quantity_requested"
            ]

            inventory = inventory_map.get(
                product_id
            )

            if (
                inventory is None
                or inventory.quantity < requested_qty
            ):
                has_insufficient_stock = True
                break

        if has_insufficient_stock:

            order.status = "REJECTED"
            order.save()

            for item in items:

                OrderItem.objects.create(
                    order=order,
                    product_id=item["product_id"],
                    quantity_requested=item[
                        "quantity_requested"
                    ]
                )

            return Response(
                {
                    "order_id": order.id,
                    "status": order.status,
                },
                status=status.HTTP_201_CREATED,
            )

        # All inventory available
        for item in items:

            inventory = inventory_map[
                item["product_id"]
            ]

            inventory.quantity -= item[
                "quantity_requested"
            ]

            inventory.save(
                update_fields=["quantity"]
            )
            if inventory.quantity < 10:

                send_low_stock_alert.delay(
                    inventory.store.name,
                    inventory.product.title,
                    inventory.quantity
                )
            OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                quantity_requested=item[
                    "quantity_requested"
                ]
            )

        order.status = "CONFIRMED"
        order.save(
            update_fields=["status"]
        )

        return Response(
            {
                "order_id": order.id,
                "status": order.status,
            },
            status=status.HTTP_201_CREATED,
        )
@extend_schema(
    summary="List Store Orders",
    description="Return all orders for a store.",
    responses=OrderListSerializer(many=True),
)
class StoreOrdersAPIView(APIView):

    def get(self, request, store_id):

        orders = (
            Order.objects
            .filter(store_id=store_id)
            .annotate(
                total_items=Count("items")
            )
            .order_by("-created_at")
        )

        serializer = OrderListSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)