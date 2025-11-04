# api/decorators.py
from functools import wraps
from django.http import JsonResponse
from django.utils.timezone import now
from .models import UserSession


def user_required(view_func):
    """Decorator for normal authenticated users (based on custom token)."""
    @wraps(view_func)
    def wrapper(s, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_header = (
            request.headers.get('Authorization')
            if hasattr(request, 'headers')
            else request.META.get('HTTP_AUTHORIZATION')
        )


        # 1️⃣ Header yo‘qligini tekshirish
        if not auth_header:
            print(auth_header)
            return JsonResponse({'detail': 'Authorization header missing'}, status=401)

        # 2️⃣ Token formatini tekshirish <token>
        token = auth_header.strip()

        # 3️⃣ Tokenni bazadan izlash
        session = UserSession.objects.filter(token=token).select_related('user').first()
        if not session:
            return JsonResponse({'detail': 'Invalid or expired token'}, status=401)

        # 4️⃣ Qurilma va IP tekshirish (faqat bitta qurilmadan foydalanish uchun)
        current_device = request.headers.get('User-Agent', 'Unknown Device')
        # current_ip = request.META.get('REMOTE_ADDR')

        if session.device_info != current_device:
            return JsonResponse({'detail': 'Access denied: token is not valid for this device.'}, status=403)

        # 5️⃣ Token amal qilish muddati (agar kerak bo‘lsa)
        # masalan, 7 kunlik cheklov uchun (ixtiyoriy)
        # if (now() - session.created_at).days > 7:
        #     return JsonResponse({'detail': 'Token expired'}, status=401)

        # 6️⃣ request.user ni biriktirish
        request.user = session.user
        return view_func(s, request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator for admin users only."""

    """Decorator for normal authenticated users (based on custom token)."""
    @wraps(view_func)
    def wrapper(s, request, *args, **kwargs):
        auth_header = (
            request.headers.get('Authorization')
            if hasattr(request, 'headers')
            else request.META.get('HTTP_AUTHORIZATION')
        )


        # 1️⃣ Header yo‘qligini tekshirish
        if not auth_header:
            print(auth_header)
            return JsonResponse({'detail': 'Authorization header missing'}, status=401)

        # 2️⃣ Token formatini tekshirish <token>
        token = auth_header.strip()

        # 3️⃣ Tokenni bazadan izlash
        session = UserSession.objects.filter(token=token).select_related('user').first()
        if not session:
            return JsonResponse({'detail': 'Invalid or expired token'}, status=401)

        # 4️⃣ Qurilma va IP tekshirish (faqat bitta qurilmadan foydalanish uchun)
        current_device = request.headers.get('User-Agent', 'Unknown Device')
        # current_ip = request.META.get('REMOTE_ADDR')

        if session.device_info != current_device:
            return JsonResponse({'detail': 'Access denied: token is not valid for this device.'}, status=403)

        # 5️⃣ Token amal qilish muddati (agar kerak bo‘lsa)
        # masalan, 7 kunlik cheklov uchun (ixtiyoriy)
        # if (now() - session.created_at).days > 7:
        #     return JsonResponse({'detail': 'Token expired'}, status=401)

        # 6️⃣ request.user ni biriktirish
        request.user = session.user
        user = request.user
        # Foydalanuvchi admin ekanligini tekshirish
        # (sizning User modelda "is_staff" yoki "role" bo'lishiga qarab)
        if not getattr(user, "is_staff", False) and getattr(user, "role", "").upper() != "ADMIN":
            return JsonResponse({'detail': 'Admin privileges required'}, status=403)

        request.user = user
        session.updated_at = now()
        session.save()
        return view_func(s, request, *args, **kwargs)
    return wrapper
