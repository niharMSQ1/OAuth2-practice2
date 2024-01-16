from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def dummyApi(request):
    return JsonResponse(
        {
            "status":"Success",
            "message":"All good here....."
        }
    )