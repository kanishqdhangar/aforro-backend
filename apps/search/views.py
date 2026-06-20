from django.db.models import Q, Sum, F, Case, When, Value, IntegerField

from rest_framework.generics import ListAPIView

from apps.products.models import Product

from .serializers import (
    ProductSearchSerializer
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ProductSearchAPIView(
    ListAPIView
):

    serializer_class = (
        ProductSearchSerializer
    )

    def get_queryset(self):

        queryset = (
            Product.objects
            .select_related("category")
            .all()
        )

        q = self.request.GET.get("q")

        category = self.request.GET.get(
            "category"
        )

        min_price = self.request.GET.get(
            "min_price"
        )

        max_price = self.request.GET.get(
            "max_price"
        )

        store_id = self.request.GET.get(
            "store_id"
        )

        sort = self.request.GET.get(
            "sort"
        )

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                |
                Q(description__icontains=q)
            )

        if category:
            queryset = queryset.filter(
                category__name__iexact=category
            )

        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

        if store_id:
            queryset = queryset.filter(
                inventory__store_id=store_id
            )

        queryset = queryset.annotate(
            available_quantity=Sum(
                "inventory__quantity"
            )
        )

        if sort == "price":
            queryset = queryset.order_by(
                "price"
            )

        elif sort == "-price":
            queryset = queryset.order_by(
                "-price"
            )

        elif sort == "title":
            queryset = queryset.order_by(
                "title"
            )

        elif sort == "-title":
            queryset = queryset.order_by(
                "-title"
            )

        queryset = queryset.annotate(
            available_quantity=Sum(
                "inventory__quantity"
            )
        )

        return queryset


class ProductSuggestAPIView(APIView):

    def get(self, request):

        q = request.GET.get("q", "").strip()

        if len(q) < 3:
            return Response(
                {
                    "detail":
                    "Minimum 3 characters required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        suggestions = (
            Product.objects
            .filter(
                Q(title__icontains=q)
            )
            .annotate(
                match_priority=Case(
                    When(
                        title__istartswith=q,
                        then=Value(0),
                    ),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by(
                "match_priority",
                "title",
            )
            .values_list(
                "title",
                flat=True,
            )[:10]
        )

        return Response(
            {
                "results": list(suggestions)
            }
        )