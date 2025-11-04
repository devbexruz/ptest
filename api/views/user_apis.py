from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from api.models import Ticket
from api.serializers import TicketSerializer




