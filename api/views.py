from django.shortcuts import render
from rest_framework import viewsets

from api.models import (
    User,
    Test,
    Image,
    Theme,
    Ticket,
    Variant
)
from api.serializers import (
    UserSerializer,
    ImageSerializer,
    TestSerializer,
    ThemeSerializer,
    TicketSerializer,
    VariantSerializer
)

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    # For User
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ThemeViewSet(viewsets.ModelViewSet):
    # For Theme
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

class TicketViewSet(viewsets.ModelViewSet):
    # For Ticket
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class VariantViewSet(viewsets.ModelViewSet):
    # For Variant
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

class TestViewSet(viewsets.ModelViewSet):
    # For Test
    queryset = Test.objects.all()
    serializer_class = TestSerializer

class ImageViewSet(viewsets.ModelViewSet):
    # For Image
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

