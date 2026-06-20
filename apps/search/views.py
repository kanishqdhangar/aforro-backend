from django.db.models import Q, Sum, F, Case, When, Value, IntegerField

from rest_framework.generics import ListAPIView

from apps.products.models import Product

from .serializers import (
    ProductSearchSerializer
)
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .rate_limit import is_rate_limited

class ProductSearchAPIView(APIView):

    def get(self, request):

        cache_key = (
            "product_search:"
            + request.get_full_path()
        )

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = self.get_queryset(request)

        serializer = ProductSearchSerializer(
            queryset,
            many=True
        )

        data = serializer.data

        cache.set(
            cache_key,
            data,
            timeout=300
        )

        return Response(data)

    def get_queryset(self, request):

        queryset = (
            Product.objects
            .select_related("category")
            .all()
        )

        q = request.GET.get("q")

        category = request.GET.get(
            "category"
        )

        min_price = request.GET.get(
            "min_price"
        )

        max_price = request.GET.get(
            "max_price"
        )

        store_id = request.GET.get(
            "store_id"
        )

        sort = request.GET.get(
            "sort"
        )

        in_stock = request.GET.get("in_stock")

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                |
                Q(description__icontains=q)
                |
                Q(category__name__icontains=q)
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
        elif sort == "newest":
            queryset = queryset.order_by("-created_at")
        if in_stock == "true":
            queryset = queryset.filter(
                available_quantity__gt=0
            )

        return queryset

class ProductSuggestAPIView(APIView):
    def get_client_ip(
        self,
        request
    ):
        x_forwarded_for = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]

        return request.META.get(
            "REMOTE_ADDR"
        )
    def get(self, request):
        ip_address = self.get_client_ip(
            request
        )

        if is_rate_limited(
            ip_address
        ):
            return Response(
                {
                    "detail":
                    "Rate limit exceeded. Try again later."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
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