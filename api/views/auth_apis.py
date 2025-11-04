from django.contrib.auth import authenticate, logout
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.serializers import LoginSerializer
from api.utils import generate_token
from api.models import UserSession
from rest_framework.views import APIView
from api.decorators import user_required

# Imports for swagger
from drf_spectacular.utils import extend_schema
from abc import ABC, abstractmethod

# Auth (Admin, User)
##############################
# swagger-tag: Student Market
@extend_schema(tags=["Auth Apis"])
class AuthApis(APIView):
    pass

# Login Api
class LoginView(AuthApis):
    @extend_schema(
        request=LoginSerializer,
        responses={200: {'token': 'string'}},
        description="Login user (only one device allowed)"
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is None:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

            # Qurilma va IP ma’lumotlarini olish
            device_info = request.headers.get('User-Agent', 'Unknown Device')
            ip_address = request.META.get('REMOTE_ADDR', None)

            # 🔒 Agar userda allaqachon token bo‘lsa, loginni bloklaymiz
            existing_session = UserSession.objects.filter(user=user).first()
            if existing_session:
                # Qurilma ma’lumotlari mos emasligini tekshiramiz
                if existing_session.device_info is None:
                    existing_session.device_info = device_info
                    existing_session.save()
                    return Response(
                        {'message': 'Login successful', 'token': str(existing_session.token)},
                        status=status.HTTP_200_OK
                    )
                elif (existing_session.device_info != device_info):
                    return Response(
                        {'detail': 'This account is already logged in from another device.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                else:
                    existing_session.device_info = device_info
                    existing_session.save()
                    return Response(
                        {'message': 'You are already logged in.', 'token': str(existing_session.token)},
                        status=status.HTTP_200_OK
                    )

            # Token yaratish
            token = generate_token(ip_address)
            UserSession.objects.create(
                user=user,
                token=token,
                device_info=device_info,
                ip_address=ip_address,
            )

            return Response(
                {'token': token, 'message': 'Login successful'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(AuthApis):
    @user_required
    def post(self, request):
        print(request.headers.get('Authorization'))
        user = request.user
        try:
            session = UserSession.objects.get(user=user)
            session.device_info = None
            session.save()
            return Response({'message': 'Logged out successfully'})
        except:
            return Response({'detail': 'You are not logged in.'}, status=status.HTTP_400_BAD_REQUEST)
