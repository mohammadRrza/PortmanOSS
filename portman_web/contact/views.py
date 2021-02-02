import sys, os
from datetime import time
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from rest_framework import status, views, mixins, viewsets, permissions
from router import utility
from router.models import Router
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated
from router.serializers import RouterSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = max