from django.urls import path

from .views import (
    ProductSearchAPIView, 
    ProductSuggestAPIView
)

urlpatterns = [
    path(
        "products/",
        ProductSearchAPIView.as_view(),
    ),
    path(
        "suggest/",
        ProductSuggestAPIView.as_view(),
    ),
]