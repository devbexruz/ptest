from django.urls import path

# U S E R S
#############################################################################################
# User Imports


# User Urls
urlpatterns = [

]

# A D M I N
#############################################################################################
# Admin Imports
from api.views.admin_apis import (
    # User imports
    UserView,
    UserByIdView,
    
    # Theme imports
    ThemeView,
    ThemeByIdView,

    # Ticket imports
    TicketView,
    TicketByIdView,

    # Test imports
    TestView,
    TestByIdView,

    # Test Variant imports
    TestVariantView,
    TestVariantByIdView,
    VariantIsTrueView
)

# Admin Urls
urlpatterns += [
    # User urls
    path("admin/user/", UserView.as_view(), name="User-get-all-create"),
    path("admin/user/<int:pk>/", UserByIdView.as_view(), name="User-get-update-delete"),
    
    # Theme urls
    path("admin/theme/", ThemeView.as_view(), name="Theme-get-all-create"),
    path("admin/theme/<int:pk>/", ThemeByIdView.as_view(), name="Theme-get-update-delete"),

    # Ticket urls
    path("admin/ticket/", TicketView.as_view(), name="Ticket-get-all-create"),
    path("admin/ticket/<int:pk>/", TicketByIdView.as_view(), name="Ticket-get-update-delete"),

    # Test urls
    path("admin/test/", TestView.as_view(), name="Test-get-all-create"),
    path("admin/test/<int:pk>/", TestByIdView.as_view(), name="Test-get-update-delete"),

    # Test Variant urls
    path("admin/test/<int:test_id>/variant/", TestVariantView.as_view(), name="Test-variant-get-all-create"),
    path("admin/test/variant/<int:pk>/", TestVariantByIdView.as_view(), name="Test-variant-get-update-delete"),
    # True Variant select url
    path("admin/test/variant/<int:pk>/true/", VariantIsTrueView.as_view(), name="Test-variant-true-select"),
]


# A U T H
#############################################################################################
# Auth Imports
from api.views.auth_apis import (
    LoginView,
    LogoutView,
)

# Auth Urls
urlpatterns += [
    path("auth/login/", LoginView.as_view(), name="Login"),
    path("auth/logout/", LogoutView.as_view(), name="Logout")
]