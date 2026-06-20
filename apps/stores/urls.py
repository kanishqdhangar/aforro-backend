from django.urls import path

from .views import (
    StoreInventoryAPIView
)
from apps.orders.views import StoreOrdersAPIView
urlpatterns = [
    path(
        "<int:store_id>/inventory/",
        StoreInventoryAPIView.as_view(),
    ),
    path(
        "<int:store_id>/orders/",
        StoreOrdersAPIView.as_view(),
    ),
]