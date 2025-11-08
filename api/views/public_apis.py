
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
            telegram_link = Data.objects.create(key="telegram_link", value="https://t.me/bexruzdeveloper")
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
    def put(self, request):
        serializer = DataSerializer(data=request.data)
        try:
            data = Data.objects.get(key=serializer.validated_data["key"])
            data.value = serializer.validated_data["value"]
            data.save()
            return Response({
                "message": "Data updated successfully",
                "data": serializer.data
            })
        except Data.DoesNotExist:
            return Response({"detail": "Data not found"}, status=status.HTTP_404_NOT_FOUND)
        

