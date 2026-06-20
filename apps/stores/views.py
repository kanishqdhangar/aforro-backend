from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Inventory
from .serializers import (
    InventoryListSerializer
)


class StoreInventoryAPIView(APIView):

    def get(self, request, store_id):

        inventory = (
            Inventory.objects
            .select_related(
                "product",
                "product__category"
            )
            .filter(
                store_id=store_id
            )
            .order_by(
                "product__title"
            )
        )

        serializer = InventoryListSerializer(
            inventory,
            many=True
        )

        return Response(
            serializer.data
        )