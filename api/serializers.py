from rest_framework import serializers
from api.models import (
    User,
    Test,
    Image,
    Theme,
    Ticket,
    Variant
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_superuser', 'is_staff', 'is_active', )
        write_only_fields = ('password', )

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = '__all__'
