# timezon
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from api.models import (
    Theme,
    Ticket,
    TestSheet,
    User,
    Test, 
    Result,
    Variant
)
from api.serializers import (
    UserSerializer,
    ThemeSerializer,
    TicketSerializer,

)

from api.decorators import user_required


# Get Profile
@extend_schema(tags=["User Apis"])
class UserApis(APIView):
    pass
class Profile(UserApis):
    @extend_schema(
        responses={200: UserSerializer},
        description="Get user profile"
    )
    @user_required
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        description="Update user profile"
    )
    @user_required
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class GetThemes(UserApis):
    @extend_schema(
        responses={200: ThemeSerializer},
        description="Get user themes"
    )
    @user_required
    def get(self, request):
        all_themes = Theme.objects.all()
        serializer = ThemeSerializer(all_themes, many=True)
        return Response(serializer.data)


class GetTickets(UserApis):
    @extend_schema(
        responses={200: TicketSerializer},
        description="Get user tickets"
    )
    @user_required
    def get(self, request):
        all_tickets = Ticket.objects.all()
        serializer = TicketSerializer(all_tickets, many=True)
        return Response(serializer.data)




from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from random import sample
from api.models import Test, Result, TestSheet, Theme, Ticket
from django.contrib.auth import get_user_model
from api import enums

User = get_user_model()

# --------------------
# Serializers
# --------------------
class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'


# --------------------
# ViewSet
# --------------------
@extend_schema(tags=["User Apis"])
class StartTestViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    @user_required
    def start_theme(self, request):
        """
        Theme bo'yicha test boshlash
        Body: { "theme_id": int }
        """
        theme_id = request.data.get("theme_id")
        theme = get_object_or_404(Theme, id=theme_id)

        # Barcha aktiv testlar theme bo'yicha
        tests = Test.objects.filter(theme=theme, active=True)
        if not tests.exists():
            return Response({"error": "Bu mavzuda testlar mavjud emas"}, status=400)

        result = Result.objects.create(
            user=request.user,
            description=f"Theme {theme.name}",
            test_length=tests.count(),
            true_answers=0,
            test_type=enums.TestChoices.THEME
        )

        # TestSheet lar generatsiya
        for t in tests:
            TestSheet.objects.create(result=result, test=t)

        serializer = ResultSerializer(result)
        return Response(serializer.data, status=201)


    @action(detail=False, methods=['post'])
    @user_required
    def start_ticket(self, request):
        """
        Ticket bo'yicha test boshlash
        Body: { "ticket_id": int }
        """
        ticket_id = request.data.get("ticket_id")
        ticket = get_object_or_404(Ticket, id=ticket_id)
        tests = Test.objects.filter(ticket=ticket, active=True)
        if not tests.exists():
            return Response({"error": "Bu biletga testlar mavjud emas"}, status=400)

        result = Result.objects.create(
            user=request.user,
            description=f"Ticket {ticket.name}",
            test_length=tests.count(),
            true_answers=0,
            test_type=enums.TestChoices.TICKET
        )

        for t in tests:
            TestSheet.objects.create(result=result, test=t)

        serializer = ResultSerializer(result)
        return Response(serializer.data, status=201)


    @action(detail=False, methods=['post'])
    @user_required
    def start_settest(self, request):
        """
        SetTest bo'yicha test boshlash
        Body: { "count": int }
        """
        count = int(request.data.get("count", 20))
        tests = Test.objects.filter(active=True)
        if tests.count() < count:
            return Response({"error": f"Faqat {tests.count()} ta test mavjud"}, status=400)

        selected_tests = sample(list(tests), count)

        result = Result.objects.create(
            user=request.user,
            description=f"SetTest {count} ta test",
            test_length=count,
            true_answers=0,
            test_type=enums.TestChoices.SETTEST
        )

        for t in selected_tests:
            TestSheet.objects.create(result=result, test=t)

        serializer = ResultSerializer(result)
        return Response(serializer.data, status=201)


    @action(detail=False, methods=['post'])
    @user_required
    def start_exam(self, request):
        """
        Exam bo'yicha test boshlash
        Body: { "count": int = 20 }
        """
        count = int(request.data.get("count", 20))
        tests = Test.objects.filter(active=True)
        if tests.count() < count:
            return Response({"error": f"Faqat {tests.count()} ta test mavjud"}, status=400)

        selected_tests = sample(list(tests), count)

        result = Result.objects.create(
            user=request.user,
            description=f"Exam {count} ta test",
            test_length=count,
            true_answers=0,
            test_type=enums.TestChoices.EXAM
        )

        for t in selected_tests:
            TestSheet.objects.create(result=result, test=t)

        serializer = ResultSerializer(result)
        return Response(serializer.data, status=201)
    


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import Result, TestSheet, Variant

@extend_schema(tags=["User Apis"])
class SolveTestViewSet(viewsets.ViewSet):
    @action(detail=True, methods=['post'])
    @user_required
    def answer(self, request, pk=None):
        """
        TestSheet ga variantni belgilash
        Body: { "variant_id": int }
        """
        testsheet = get_object_or_404(TestSheet, id=pk, result__user=request.user)
        variant_id = request.data.get("variant_id")
        variant = get_object_or_404(Variant, id=variant_id, test=testsheet.test)

        testsheet.current_answer = variant
        testsheet.selected = True
        testsheet.successful = (variant == testsheet.test.correct_answer)
        testsheet.save()

        return Response({
            "message": "Javob saqlandi",
            "testsheet_id": testsheet.id,
            "successful": testsheet.successful
        })


    @action(detail=True, methods=['post'])
    @user_required
    def finish(self, request, pk=None):
        """
        Result ni tugatish
        """
        result = get_object_or_404(Result, id=pk, user=request.user)
        if result.finished:
            return Response({"error": "Test allaqachon tugatilgan"}, status=400)

        # To'g'ri javoblarni hisoblash
        true_answers = TestSheet.objects.filter(result=result, successful=True).count()
        result.true_answers = true_answers
        result.finished = True
        result.end_time = timezone.now()
        result.save()

        return Response({
            "message": "Test tugatildi",
            "result_id": result.id,
            "true_answers": true_answers,
            "test_length": result.test_length
        })


# api/views/user_apis.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from api.models import TestSheet, Variant
from api.serializers import VariantSerializer



@extend_schema(tags=["User Apis"])
class SolveTestDetailView(APIView):
    
    @user_required
    def get(self, request, result_id):
        # Faqat foydalanuvchiga tegishli TestSheetlarni olish
        testsheets = TestSheet.objects.filter(result__id=result_id, result__user=request.user).all()
        data = []

        for ts in testsheets:
            variants = Variant.objects.filter(test=ts.test)
            data.append({
                "id": ts.test.id,
                "value": ts.test.value,
                "variants": VariantSerializer(variants, many=True).data
            })
        return Response(data)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserStatisticsView(APIView):
    """
    GET /api/statistics/
    """
    @user_required
    def get(self, request):
        user = request.user
        results = Result.objects.filter(user=user)

        total_tests = results.count()
        total_correct = sum(r.true_answers for r in results)
        total_incorrect = total_correct - sum(r.true_answers for r in results)
        total_questions = total_correct + total_incorrect
        avg_score = round(sum(r.true_answers for r in results) / total_tests, 1) if total_tests > 0 else 0
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
