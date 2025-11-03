from django.urls import path
from api.views import (
    UserViewSet,
    ImageViewSet,
    TestViewSet,
    ThemeViewSet,
    TicketViewSet,
    VariantViewSet
)

urlpatterns = [
    # User Viewsets
    path("get_users", UserViewSet.as_view({"get": "list"})),
    path("get_user/<int:pk>", UserViewSet.as_view({"get": "retrieve"})),
    path("create_user", UserViewSet.as_view({"post": "create"})),
    path("update_user/<int:pk>", UserViewSet.as_view({"put": "update"})),
    path("delete_user/<int:pk>", UserViewSet.as_view({"delete": "destroy"})),
    # Image Viewsets
    path("get_images", ImageViewSet.as_view({"get": "list"})),
    path("get_image/<int:pk>", ImageViewSet.as_view({"get": "retrieve"})),
    path("create_image", ImageViewSet.as_view({"post": "create"})),
    path("update_image/<int:pk>", ImageViewSet.as_view({"put": "update"})),
    path("delete_image/<int:pk>", ImageViewSet.as_view({"delete": "destroy"})),
    # Test Viewsets
    path("get_tests", TestViewSet.as_view({"get": "list"})),
    path("get_test/<int:pk>", TestViewSet.as_view({"get": "retrieve"})),
    path("create_test", TestViewSet.as_view({"post": "create"})),
    path("update_test/<int:pk>", TestViewSet.as_view({"put": "update"})),
    path("delete_test/<int:pk>", TestViewSet.as_view({"delete": "destroy"})),
    # Theme Viewsets
    path("get_themes", ThemeViewSet.as_view({"get": "list"})),
    path("get_theme/<int:pk>", ThemeViewSet.as_view({"get": "retrieve"})),
    path("create_theme", ThemeViewSet.as_view({"post": "create"})),
    path("update_theme/<int:pk>", ThemeViewSet.as_view({"put": "update"})),
    path("delete_theme/<int:pk>", ThemeViewSet.as_view({"delete": "destroy"})),
    # Ticket Viewsets
    path("get_tickets", TicketViewSet.as_view({"get": "list"})),
    path("get_ticket/<int:pk>", TicketViewSet.as_view({"get": "retrieve"})),
    path("create_ticket", TicketViewSet.as_view({"post": "create"})),
    path("update_ticket/<int:pk>", TicketViewSet.as_view({"put": "update"})),
    path("delete_ticket/<int:pk>", TicketViewSet.as_view({"delete": "destroy"})),
    # Variant Viewsets
    path("get_variants", VariantViewSet.as_view({"get": "list"})),
    path("get_variant/<int:pk>", VariantViewSet.as_view({"get": "retrieve"})),
    path("create_variant", VariantViewSet.as_view({"post": "create"})),
    path("update_variant/<int:pk>", VariantViewSet.as_view({"put": "update"})),
    path("delete_variant/<int:pk>", VariantViewSet.as_view({"delete": "destroy"})),

]
