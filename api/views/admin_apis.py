# Admin
from django.contrib.auth import authenticate, logout
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, parsers
from rest_framework.permissions import IsAuthenticated
from api.serializers import (
    # User serializers
    CreateUserSerializer,
    GetUserSerializer,
    UpdateUserSerializer,

    # Theme serializers
    CreateThemeSerializer,
    GetThemeSerializer,
    UpdateThemeSerializer,

    # Ticket serializers
    CreateTicketSerializer,
    GetTicketSerializer,
    UpdateTicketSerializer,

    # Test serializers
    CreateTestSerializer,
    GetTestSerializer,
    UpdateTestSerializer,
    UploadTestImageSerializer,

    # Test Variant serializers
    CreateVariantSerializer,
    GetVariantSerializer,
    UpdateVariantSerializer,
    # Data
    ClearUserResultsSerializer
)
from api.utils import generate_token
from rest_framework.views import APIView
from api.decorators import user_required, admin_required

# Import Models
from api.models import (
    UserSession,
    User,
    Test,
    Theme,
    Ticket,
    TestSheet,
    Variant,
    Result

)
from api import enums

# Imports for swagger
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from abc import ABC, abstractmethod

# Admin User
##############################
# swagger-tag: Admin User
@extend_schema(tags=["Admin User"])
class AdminUser(APIView):
    pass


# User (Create, Get All)
class UserView(AdminUser):
    @extend_schema(
        request=CreateUserSerializer,
        responses={201: {'message': 'User created successfully'}},
        description="Create a new user"
    )
    @admin_required
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            full_name = serializer.validated_data['full_name']
            user = User.objects.create_user(username=username, password=password, full_name=full_name)
            return Response({'message': 'User created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        responses={200: GetUserSerializer(many=True)},
        description="Get all users"
    )
    @admin_required
    def get(self, request):
        users = User.objects.all()
        serializer = GetUserSerializer(users, many=True)
        return Response(serializer.data)


# User by id (Get, Update, Delete)
class UserByIdView(AdminUser):
    @extend_schema(
        responses={200: GetUserSerializer},
        description="Get user by id"
    )
    @admin_required
    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            serializer = GetUserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=UpdateUserSerializer,
        responses={200: GetUserSerializer},
        description="Update user by id"
    )
    @admin_required
    def put(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            if user.id == request.user.id:
                return Response({'detail': "O\'zingizni ham o\'zgartirishingiz mumkin"}, status=status.HTTP_400_BAD_REQUEST)
            if user.is_staff:
                return Response({'detail': "Super userni o'zgartirish mumkin emas"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: GetUserSerializer},
        description="Delete user by id"
    )
    @admin_required
    def delete(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            if user.id == request.user.id:
                return Response({'detail': 'You cannot delete yourself'}, status=status.HTTP_400_BAD_REQUEST)
            if user.is_staff:
                return Response({'detail': 'You cannot delete a staff user'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'message': 'User deleted successfully'})

# Get Users Statistika
class UserStatisticsView(AdminUser):
    @extend_schema(
        responses={200: GetUserSerializer(many=True)},
        description="Get all users"
    )
    @admin_required
    def get(self, request):
        users = User.objects.all()
        datas = dict()
        results = Result.objects.filter(test_type=enums.TestChoices.EXAM)
        for result in results:
            if result.user.id not in datas:
                datas[result.user.id] = {
                    "name": result.user.full_name,
                    "total_tests": 0,
                    "total_correct": 0,
                    "total_incorrect": 0,
                    "total_questions": 0,
                    "true_answers": 0,
                    "average_percent": 0,
                    "best_score": 0,
                }
            datas[result.user.id]["total_tests"] += 1
            datas[result.user.id]["total_correct"] += result.true_answers
            datas[result.user.id]["total_incorrect"] += result.incorrect_answers
            datas[result.user.id]["total_questions"] += result.test_length
            datas[result.user.id]["true_answers"] += result.true_answers
            datas[result.user.id]["best_score"] = max(datas[result.user.id]["best_score"], result.true_answers)
        result = []
        for user_id, user in datas.items():
            result.append({
                "id": user_id,
                "name": user["name"],
                "total_tests": datas[user_id]["total_tests"],
                "total_correct": datas[user_id]["total_correct"],
                "total_incorrect": datas[user_id]["total_incorrect"],
                "average_score": round(datas[user_id]["true_answers"]/datas[user_id]["total_tests"]),
                "average_percent": datas[user_id]["average_percent"],
                "total_questions": datas[user_id]["total_questions"],
                "best_score": datas[user_id]["best_score"],
            })
        return Response(result)
    # User Results Clear
    @extend_schema(
        request=ClearUserResultsSerializer,
        responses={200: {
            "message": "Results deleted successfully"
        }},
        description="Get all users"
    )
    @admin_required
    def post(self, request):
        serializer = ClearUserResultsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        Result.objects.filter(user_id=serializer.validated_data["user_id"], test_type=enums.TestChoices.EXAM).delete()
        return Response({'message': 'Results deleted successfully'})



class AdminUserStatisticsView(APIView):
    @admin_required
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        results = Result.objects.filter(test_type=enums.TestChoices.EXAM, user=user)

        total_tests = results.count()
        total_correct = sum(r.true_answers for r in results)
        total_incorrect = sum(r.incorrect_answers for r in results)
        total_questions = total_correct + total_incorrect
        avg_score = round(sum(r.true_answers for r in results) / total_tests) if total_tests > 0 else 0
        avg_percent = round((total_correct / total_questions) * 100, 1) if total_questions > 0 else 0
        best_score = max([r.true_answers for r in results], default=0)

        data = {
            "total_tests": total_tests,
            "total_correct": total_correct,
            "total_incorrect": total_incorrect,
            "total_questions": total_questions,
            "average_score": avg_score,
            "average_percent": avg_percent,
            "best_score": best_score,
        }

        return Response(data)



# Admin Mavzu
##############################
# swagger-tag: Admin Mavzu
@extend_schema(tags=["Admin Mavzu"])
class AdminMavzu(APIView):
    pass


# Mavzu (Create, Get All)
class ThemeView(AdminMavzu):
    @extend_schema(
        request=CreateThemeSerializer,
        responses={201: {'message': 'Theme created successfully'}},
        description="Create a new theme"
    )
    @admin_required
    def post(self, request):
        serializer = CreateThemeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Theme created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: GetThemeSerializer(many=True)},
        description="Get all themes"
    )
    @admin_required
    def get(self, request):
        themes = Theme.objects.all()
        serializer = GetThemeSerializer(themes, many=True)
        return Response(serializer.data)

# Mavzu by id (Get, Update, Delete)
class ThemeByIdView(AdminMavzu):
    @extend_schema(
        responses={200: GetThemeSerializer},
        description="Get theme by id"
    )
    @admin_required
    def get(self, request, pk):
        try:
            theme = Theme.objects.get(id=pk)
            serializer = GetThemeSerializer(theme)
            return Response(serializer.data)
        except Theme.DoesNotExist:
            return Response({'detail': 'Theme not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=UpdateThemeSerializer,
        responses={200: GetThemeSerializer},
        description="Update theme by id"
    )
    @admin_required
    def put(self, request, pk):
        try:
            theme = Theme.objects.get(id=pk)
        except Theme.DoesNotExist:
            return Response({'detail': 'Theme not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateThemeSerializer(theme, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: GetThemeSerializer},
        description="Delete theme by id"
    )
    @admin_required
    def delete(self, request, pk):
        try:
            theme = Theme.objects.get(id=pk)
        except Theme.DoesNotExist:
            return Response({'detail': 'Theme not found'}, status=status.HTTP_404_NOT_FOUND)
        theme.delete()
        return Response({'message': 'Theme deleted successfully'})


# Ticket
##############################
# swagger-tag: Ticket
@extend_schema(tags=["Admin Ticket"])
class AdminTicket(APIView):
    pass

# Ticket (Create, Get All)
class TicketView(AdminTicket):
    @extend_schema(
        request=CreateTicketSerializer,
        responses={201: {'message': 'Ticket created successfully'}},
        description="Create a new ticket"
    )
    @admin_required
    def post(self, request):
        serializer = CreateTicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Ticket created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: GetTicketSerializer(many=True)},
        description="Get all tickets"
    )
    @admin_required
    def get(self, request):
        tickets = Ticket.objects.all()
        serializer = GetTicketSerializer(tickets, many=True)
        return Response(serializer.data)

# Ticket by id (Get, Update, Delete)
class TicketByIdView(AdminTicket):
    @extend_schema(
        responses={200: GetTicketSerializer},
        description="Get ticket by id"
    )
    @admin_required
    def get(self, request, pk):
        try:
            ticket = Ticket.objects.get(id=pk)
            serializer = GetTicketSerializer(ticket)
            return Response(serializer.data)
        except Ticket.DoesNotExist:
            return Response({'detail': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=UpdateTicketSerializer,
        responses={200: GetTicketSerializer},
        description="Update ticket by id"
    )
    @admin_required
    def put(self, request, pk):
        try:
            ticket = Ticket.objects.get(id=pk)
        except Ticket.DoesNotExist:
            return Response({'detail': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateTicketSerializer(ticket, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: GetTicketSerializer},
        description="Delete ticket by id"
    )
    @admin_required
    def delete(self, request, pk):
        try:
            ticket = Ticket.objects.get(id=pk)
        except Ticket.DoesNotExist:
            return Response({'detail': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
        ticket.delete()
        return Response({'message': 'Ticket deleted successfully'})

# Test
##############################
# swagger-tag: Test
@extend_schema(tags=["Admin Test"])
class AdminTest(APIView):
    pass

# Test (Create, Get All)
class TestView(AdminTest):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @extend_schema(
        request=CreateTestSerializer,
        responses={201: {'message': 'Test created successfully'}},
        description="Create a new test"
    )
    @admin_required
    def post(self, request):
        serializer = CreateTestSerializer(data=request.data) 
        if serializer.is_valid():
            # Rasm va boshqa ma'lumotlar avtomatik saqlanadi
            new_test = serializer.save()
                 
            return Response(
                {'message': 'Test created successfully', 'data': GetTestSerializer(new_test).data}, 
                status=status.HTTP_201_CREATED
            )
        
        # Xatoning aniq sababini ko'rish uchun!
        print("Serializer xatoliklari:", serializer.errors)
        
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        responses={200: GetTestSerializer(many=True)},
        description="Get all tests"
    )
    @admin_required
    def get(self, request):
        tests = Test.objects.all()
        serializer = GetTestSerializer(tests, many=True)
        return Response(serializer.data)
class TestByIdView(AdminTest):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @extend_schema(
        responses={200: GetTestSerializer},
        description="Get test by id"
    )
    @admin_required
    def get(self, request, pk):
        try:
            test = Test.objects.get(id=pk)
            serializer = GetTestSerializer(test)
            return Response(serializer.data)
        except Test.DoesNotExist:
            return Response({'detail': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=UpdateTestSerializer,
        responses={200: GetTestSerializer},
        description="Update test by id"
    )
    @admin_required
    def put(self, request, pk):
        try:
            test = Test.objects.get(id=pk)
        except Test.DoesNotExist:
            return Response({'detail': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateTestSerializer(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: GetTestSerializer},
        description="Delete test by id"
    )
    @admin_required
    def delete(self, request, pk):
        
        try:
            test = Test.objects.get(id=pk)
        except Test.DoesNotExist:
            return Response({'detail': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
        test.delete()
        return Response({'message': 'Test deleted successfully'})

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Test uchun rasm fayli'
                    }
                }
            }
        },
        responses={200: {'message': 'Test Image Uploaded'}},
        description="Test Image Upload"
    )
    @admin_required
    def patch(self, request, pk):
        try:
            test = Test.objects.get(id=pk)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if 'image' not in request.FILES:
            test.image = None
            test.save()
            return Response({'message': 'Test Image Removed'})
            # return Response({'detail': 'Image fayl yuborilmadi'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        # Fayl turini tekshirish
        allowed_content_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
        if image_file.content_type not in allowed_content_types:
            return Response({
                'detail': f'Qo\'llab-quvvatlanmaydigan fayl formati. Faqat {", ".join(allowed_content_types)} formatlari qabul qilinadi'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Fayl hajmini tekshirish (5MB)
        if image_file.size > 5 * 1024 * 1024:
            return Response({
                'detail': 'Fayl hajmi 5MB dan katta bo\'lmasligi kerak'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Faylni saqlash
        try:
            test.image = image_file
            test.save()
            return Response({'message': 'Test Image Uploaded'})
        except Exception as e:
            return Response({'detail': f'Rasm saqlanmadi: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


# Test Variant
#################
# swagger-tag: Test Variant
@extend_schema(tags=['Admin Test Variant'])
class AdminTestVariant(APIView):
    pass

class TestVariantView(AdminTestVariant):
    @extend_schema(
        request=CreateVariantSerializer,
        responses={200: GetVariantSerializer},
        description="Create a new test variant"
    )
    @admin_required
    def post(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['test_id'] = test_id
        serializer = CreateVariantSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Test variant created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        responses={200: GetVariantSerializer},
        description="Get all test variants"
    )
    @admin_required
    def get(self, request, test_id):
        variants = Variant.objects.filter(test_id=test_id).all()
        serializer = GetVariantSerializer(variants, many=True)
        return Response(serializer.data)

class TestVariantByIdView(AdminTestVariant):
    @extend_schema(
        responses={200: GetVariantSerializer},
        description="Get test variant by id"
    )
    @admin_required
    def get(self, request, pk):
        try:
            variant = Variant.objects.get(id=pk)
            serializer = GetVariantSerializer(variant)
            return Response(serializer.data)
        except Variant.DoesNotExist:
            return Response({'detail': 'Test variant not found'}, status=status.HTTP_404_NOT_FOUND)
    @extend_schema(
        request=UpdateVariantSerializer,
        responses={200: GetVariantSerializer},
        description="Update test variant by id"
    )
    @admin_required
    def put(self, request, pk):
        try:
            variant = Variant.objects.get(id=pk)
        except Variant.DoesNotExist:
            return Response({'detail': 'Test variant not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateVariantSerializer(variant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        responses={200: GetVariantSerializer},
        description="Delete test variant by id"
    )
    @admin_required
    def delete(self, request,pk):
        try:
            variant = Variant.objects.get(id=pk)
        except Variant.DoesNotExist:
            return Response({'detail': 'Test variant not found'}, status=status.HTTP_404_NOT_FOUND)
        variant.delete()
        return Response({'message': 'Test variant deleted successfully'})


class VariantIsTrueView(AdminTestVariant):
    @extend_schema(
        responses={200: GetVariantSerializer},
        description="Set is_true for variant"
    )
    @admin_required
    def post(self, request, pk):
        try:
            variant = Variant.objects.get(id=pk)
        except Variant.DoesNotExist:
            return Response({'detail': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
        variant.test.correct_answer = variant
        variant.test.active = True
        variant.test.save()
        return Response({'message': 'Variant is_true set successfully'})

class StatisticsView(AdminTestVariant):

    @admin_required
    def get(self, resuest):
        # Jami Foydalanuvchilar
        # 0

        # Jami Mavzular
        # 0

        # Jami Biletlar
        # 0

        # Jami Testlar
        # 0
        result = dict()
        result['users'] = User.objects.count()
        result['themes'] = Theme.objects.count()
        result['tickets'] = Ticket.objects.count()
        result['tests'] = Test.objects.count()
        return Response(result)
