from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *

import json

# Create your views here.
@csrf_exempt
@api_view(['POST'])
def register(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            if not username or not email or not password:
                return JsonResponse(
                    {
                    "status":"Failed",
                    "message":"Insufficient data"
                    }, 
                status = status.HTTP_400_BAD_REQUEST
                )
            
            saveUser = User.objects.create_user(email = email, username = username, password = password)
            
            return JsonResponse(
                {
                    "status":"Success",
                    "message":"User registered successfully..."
                },
                status = status.HTTP_201_CREATED
            )
        else:
            raise Exception("Incorrect method")

    except Exception as ex:
        return JsonResponse(
            {
                "status":"Failed",
                "message":str(ex)
            }
        )

@csrf_exempt
@api_view(['POST'])
def login(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse(
                    {
                    "status":"Failed",
                    "message":"Insufficient data"
                    }, 
                status = status.HTTP_400_BAD_REQUEST
                )
    
    user = authenticate(request, username = username, password = password)

    if not user:
        return JsonResponse(
            {
                "status":"failed",
                "message":"Invalid credentials"
            },
            status = status.HTTP_400_BAD_REQUEST
        )
    
    refresh = RefreshToken.for_user(user)

    return JsonResponse({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    },
    status = status.HTTP_200_OK
    )


def callTheApi(request):
    return