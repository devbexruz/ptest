# timezon
from django.utils import timezone
from datetime import timedelta

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
        all_themes = Theme.objects.all().order_by('name')
        serializer = ThemeSerializer(all_themes, many=True)
        return Response(serializer.data)


class GetTickets(UserApis):
    @extend_schema(
        responses={200: TicketSerializer},
        description="Get user tickets"
    )
    @user_required
    def get(self, request):
        all_tickets = Ticket.objects.all().order_by('id')
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
        
        # Old not finished tests clear
        Result.objects.filter(
            user=request.user,
            finished=False
        ).delete()
        
        # Yangi Yaratish
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

        # Old not finished tests clear
        Result.objects.filter(
            user=request.user,
            finished=False
        ).delete()

        # Yangi Yaratish
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

        # Old not finished tests clear
        Result.objects.filter(
            user=request.user,
            finished=False
        ).delete()

        # Yangi Yaratish
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

        # Old not finished tests clear
        Result.objects.filter(
            user=request.user,
            finished=False
        ).delete()

        # Yangi Yaratish
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
from datetime import datetime, timedelta
@extend_schema(tags=["User Apis"])
class SolveTestViewSet(viewsets.ViewSet):
    @action(detail=True, methods=['post'])
    @user_required
    def answer(self, request, pk=None):
        """
        TestSheet ga variantni belgilash
        Body: { "variant_id": int }
        """
        print(request.user)
        testsheet = get_object_or_404(TestSheet, id=pk, result__user=request.user)

        if testsheet.result.finished:
            return Response({"error": "Test allaqachon tugatilgan", "finished": result.finished}, status=400)
        variant_id = request.data.get("variant_id")
        variant = get_object_or_404(Variant, id=variant_id, test=testsheet.test)
        # 25 minut gacha javoblarni kirita olsin
        if testsheet.result.test_type == enums.TestChoices.EXAM and testsheet.result.start_time + timedelta(minutes=25) < timezone.now():
            result = get_object_or_404(Result, id=testsheet.result.id, user=request.user)
            if result.finished:
                return Response({"error": "Test allaqachon tugatilgan", "finished": result.finished}, status=400)

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
                "test_length": result.test_length, "finished": True
            })
        if testsheet.selected == True:
            return Response({"error": "TestSheet ga variant belgilangan"}, status=400)
        testsheet.current_answer = variant
        testsheet.selected = True
        testsheet.successful = (variant == testsheet.test.correct_answer)
        if testsheet.successful:
            testsheet.result.true_answers += 1
            testsheet.result.save()
        else:
            testsheet.result.incorrect_answers += 1
            testsheet.result.save()
        testsheet.save()
        if testsheet.result.incorrect_answers == 3 and not testsheet.successful:
            result = get_object_or_404(Result, id=testsheet.result.id, user=request.user)

            # To'g'ri javoblarni hisoblash
            true_answers = TestSheet.objects.filter(result=result, successful=True).count()
            result.true_answers = true_answers
            result.finished = True
            result.end_time = timezone.now()
            result.save()
            return Response({
                "error": "Test yakunlandi!", "finished": result.finished
            })
        return Response({
            "message": "Javob saqlandi",
            "testsheet_id": testsheet.id,
            "correct_answer": VariantSerializer(testsheet.test.correct_answer).data,
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

@extend_schema(tags=["User Apis"])
class ResultStatisticsView(APIView):
    @user_required
    def get(self, request, result_id):
        try:
            result = Result.objects.get(user=request.user, id=result_id)
            if not result.finished:
                return Response({"error": "Test tugatilmagan"}, status=400)
        except:
            return Response({"error": "Bunday test mavjud emas"}, status=400)
        data = {
            "id": result.id,
            "all": result.test_length,
            "trues": result.true_answers,
            "falses": result.incorrect_answers,
            "description": result.description,
            "ignores": result.test_length-result.true_answers-result.incorrect_answers,
            "percentage": round((100*result.true_answers)/result.test_length),
            "test_type": result.test_type,
        }
        return Response(data)

@extend_schema(tags=["User Apis"])
class AllResultsListView(APIView):
    @user_required
    def get(self, request):
        if request.user.role == enums.RoleChoices.ADMIN or request.user.is_staff:
            results = Result.objects.filter(
                finished=True,
                test_type=enums.TestChoices.EXAM
            ).order_by("-end_time")[:50]
        else:
            results = Result.objects.filter(
                user=request.user,
                finished=True,
                test_type=enums.TestChoices.EXAM
            ).order_by("-end_time")[:20]
        data = []
        for result in results:
            data.append({
                "id": result.id,
                "name": result.user.full_name,
                "all": result.test_length,
                "trues": result.true_answers,
                "end_time": result.end_time.strftime("%H:%M:%S"),
                "test_type": result.test_type,
                "status": result.true_answers >= 18
            })
        return Response(data)

# api/views/user_apis.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from api.models import TestSheet, Variant
from api.serializers import VariantSerializer
import random
# Optimallashtirilgan Kod
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Prefetch
import random

@extend_schema(tags=["User Apis"])
class SolveTestDetailView(APIView):
    
    @user_required
    def get(self, request, result_id):
        # 1. N+1 muammosini hal qilish: Faqat bitta so'rovda Test va Variantlarni oldindan yuklash
        testsheets_qs = TestSheet.objects.filter(
            result__id=result_id, 
            result__user=request.user
        ).select_related(
            'test',  # Test ob'ektini yuklaydi
            'current_answer', # Current Answer (Agar Modelda ForeignKey bo'lsa)
            'test__correct_answer' # Correct Answer (Agar Modelda ForeignKey bo'lsa)
        ).prefetch_related(
            Prefetch('test__variant_set', queryset=Variant.objects.all()) 
            # Testga tegishli barcha variantlarni bir so'rovda yuklaydi
        ).all()
        
        data = []

        # 2. Loop ichidagi DB so'rovlarini olib tashlash
        for ts in testsheets_qs:
            # Variantlarni oldindan yuklangan to'plamdan olish
            variants = list(ts.test.variant_set.all())
            
            # Agar variant_orders bo'sh bo'lsa (yoki yangi variantlar qo'shilgan bo'lsa):
            # Bu qism mantiqi GET dan POST/PATCH metodiga o'tkazilishi tavsiya etiladi!
            # Agar shunday qolishi kerak bo'lsa, 'update_fields' dan foydalaning va save() ni loopdan tashqarida qiling:
            
            # Mantiqiy xatoni tuzatish: variant_orders ni faqat kerak bo'lsa yangilash
            variant_ids_in_db = {v.id for v in variants}
            
            # Agar mavjud bo'lmasa yoki eskirgan bo'lsa, yangilash logikasi (POST/PATCH uchun yaxshiroq)
            if not ts.variant_orders or set(ts.variant_orders) != variant_ids_in_db:
                ts.variant_orders = list(variant_ids_in_db)
                random.shuffle(ts.variant_orders)
                # Barcha o'zgarishlarni to'plab, loopdan keyin saqlash afzal
                ts.save() # Qolgan kodni to'liq ko'rmaganim uchun shu yerda qoldirildi, lekin buni optimallashtirish kerak.

            # Variant tartibini olish:
            variant_map = {v.id: v for v in variants}
            # variant_orders bo'yicha to'g'ri tartiblash
            variant_new_order = [variant_map[id] for id in ts.variant_orders if id in variant_map]

            data.append({
                "id": ts.id,
                "value": ts.test.value,
                "status": ts.successful,
                # Rasm: .name tekshiruvi qo'shildi
                "image": request.build_absolute_uri(ts.test.image.url) if ts.test.image and ts.test.image.name else None,
                "current_answer": VariantSerializer(ts.current_answer).data if ts.current_answer else None,
                "correct_answer": VariantSerializer(ts.test.correct_answer).data if (ts.result.finished or ts.current_answer) else None,
                "variants": VariantSerializer(variant_new_order, many=True).data
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
