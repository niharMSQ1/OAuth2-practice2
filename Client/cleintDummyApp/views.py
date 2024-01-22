from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json

# Create your views here.
@csrf_exempt
def dummyApi(request):

    data = (json.loads(request.body)).get('data')
    square = data*data
    
    return JsonResponse({
        "status":"Success",
        "message":f"square of data is {square}"
    })
