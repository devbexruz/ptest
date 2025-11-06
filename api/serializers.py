from rest_framework import serializers
from api.models import (
    User,
    Test,
    Theme,
    Ticket,
    Variant
)

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'last_login',
            'is_superuser', 
            'username',
            'full_name',
            'role',
            'ruxsat',
        ]
        read_only_fields = ('id', 'last_login', 'ruxsat', 'role', 'username', 'is_superuser', )
        write_only_fields = ('password', )
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password, save=True)
        user.save()
        return user


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
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



# RestFull Api Serializers
from django.contrib.auth import authenticate

# Auth Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User is deactivated.")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        data['user'] = user
        return data


###############################################################################
###################### Admin Serializers ######################################

# User Serializers
#############################################################################
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'full_name']
        extra_kwargs = {'password': {'write_only': True}}

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_superuser', 'is_staff', 'is_active', )
        extra_kwargs = {'password': {'write_only': True}}
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'full_name', 'role', 'ruxsat']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # Boshqa fieldlarni yangilaymiz
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Agar parol kelgan bo‘lsa, uni shifrlaymiz
        if password:
            instance.set_password(password)

        instance.save()
        return instance








# Mavzu Serializers
#############################################################################
class CreateThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'

class GetThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'
        read_only_fields = ('id', 'created_at', )


class UpdateThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'



# Ticket Serializers
#############################################################################

class CreateTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class GetTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('id', 'created_at', )

class UpdateTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


# Test Serializers
#############################################################################

class CreateTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'correct_answer', 'active', 'image')

class GetTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ('id', 'created_at', )

class UpdateTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'image')
class UploadTestImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=False, 
        allow_null=True,
        max_length=None,  # Fayl nomi uzunligi cheklovini olib tashlash
        use_url=True
    )
    
    class Meta:
        model = Test
        fields = ['image']
        read_only_fields = ('id', 'created_at',)

    def validate_image(self, value):
        if value:
            # Fayl hajmini tekshirish (masalan, 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Rasm hajmi 5MB dan katta bo'lmasligi kerak")
            
            # Rasm formatini tekshirish
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
            ext = value.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError(f"Qo'llab-quvvatlanmaydigan format. Faqat {', '.join(valid_extensions)} formatlari qo'llab-quvvatlanadi")
        
        return value


# Variant Serializers
#############################################################################

class CreateVariantSerializer(serializers.ModelSerializer):
    test_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Variant
        fields = ['id', 'test_id', 'value']
        read_only_fields = ('id', 'created_at', 'test',)
    def create(self, validated_data):
        test_id = validated_data.pop('test_id')
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            raise serializers.ValidationError({"test_id": "Test not found"})
        
        validated_data['test'] = test
        return super().create(validated_data)

class GetVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'test', 'true_tests')

class UpdateVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'test', )

