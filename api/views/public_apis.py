
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.serializers import UserSerializer

class ProfileView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)
