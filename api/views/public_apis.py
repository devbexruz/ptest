
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.serializers import UserSerializer, DataSerializer
from api.models import Data
from rest_framework.views import APIView
from api.decorators import admin_required
from drf_spectacular.utils import extend_schema


class ProfileView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)


class ConnectionView(APIView):
    serializer_class = DataSerializer
    def get(self, request):
        try:
            telegram_link = Data.objects.get(key="telegram_link")
        except Data.DoesNotExist:
            phone_number = Data.objects.create(key="telegram_link", value="https://t.me/bexruzdeveloper")
        try:
            phone_number = Data.objects.get(key="phone_number")
        except Data.DoesNotExist:
            phone_number = Data.objects.create(key="phone_number", value="+998123456789")
        return Response({
            "telegram_link": telegram_link.value,
            "phone_number": phone_number.value
        })
    @extend_schema(
        request=DataSerializer,
        responses={200: DataSerializer},
    )
    @admin_required
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

